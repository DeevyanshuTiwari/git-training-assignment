
from __future__ import annotations

import logging
import random
from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import (
    BranchPythonOperator,
    PythonOperator,
    ShortCircuitOperator,
)
from airflow.utils.trigger_rule import TriggerRule

THREAT_THRESHOLD = int(Variable.get("zombie_threat_threshold", default_var=6))
SUPPLY_CRITICAL_THRESHOLD = int(Variable.get("zombie_supply_critical_threshold", default_var=3))

log = logging.getLogger("airflow.task")


# ---------------------------------------------------------------------------
# Task callables
# ---------------------------------------------------------------------------
def dawn_perimeter_scan(**context) -> None:
    """
    Simulate scanning the perimeter for zombie activity.

    Pushes 'threat_level' (0-10) to XCom so the branching task downstream
    can decide whether today is a fight day or a hide day.
    """
    log.debug("Beginning perimeter scan sweep of all four bunker quadrants.")

    threat_level = random.randint(0, 10)
    log.info("Perimeter scan complete. Raw threat_level=%s", threat_level)

    if threat_level >= THREAT_THRESHOLD:
        log.warning(
            "Threat level %s meets or exceeds threshold %s — hostile activity likely.",
            threat_level,
            THREAT_THRESHOLD,
        )
    else:
        log.info(
            "Threat level %s is below threshold %s — quadrant looks clear.",
            threat_level,
            THREAT_THRESHOLD,
        )

    # Push to XCom explicitly (readable/explicit, rather than relying on
    # the implicit "return value becomes XCom" behaviour).
    context["ti"].xcom_push(key="threat_level", value=threat_level)


def decide_fight_or_hide(**context) -> str:
    """
    BranchPythonOperator callable.

    Reads 'threat_level' from XCom and returns the task_id that should
    run next. Airflow automatically marks the OTHER branch as 'skipped' —
    this is our primary, story-driven deliberate skip.
    """
    threat_level = context["ti"].xcom_pull(
        task_ids="dawn_perimeter_scan", key="threat_level"
    )
    log.info("Read threat_level=%s from XCom for branching decision.", threat_level)

    if threat_level >= THREAT_THRESHOLD:
        log.warning("Branching to 'fight_zombies' — threat is too high to ignore.")
        return "fight_zombies"

    log.info("Branching to 'barricade_base' — no need to engage today.")
    return "barricade_base"


def fight_zombies(**context) -> None:
    """Simulated combat encounter. Only runs on the 'fight' branch."""
    log.critical("Engaging hostiles at the perimeter fence line!")
    log.info("Combat resolved. All survivors accounted for, minor injuries only.")


def headcount_report(**context) -> None:
    """
    Runs after the branch rejoins (regardless of which branch ran, thanks
    to trigger_rule). Pulls data from earlier tasks purely for a readable
    end-of-run summary log — useful for reconstructing what happened.
    """
    threat_level = context["ti"].xcom_pull(
        task_ids="dawn_perimeter_scan", key="threat_level"
    )
    supply_count = context["ti"].xcom_pull(task_ids="scavenge_supplies")
    log.info(
        "End-of-run summary: threat_level=%s, supply_count=%s, all survivors present.",
        threat_level,
        supply_count,
    )
    log.debug("Headcount task complete, no anomalies to escalate.")


def supplies_are_sufficient(**context) -> bool:
    """
    ShortCircuitOperator callable.

    Returns True to let downstream tasks (radio_checkin) proceed, or
    False to skip them. This is our SECOND, independent deliberate skip
    mechanism (separate from the branch above), gated on supply count
    rather than threat level.
    """
    supply_count = int(context["ti"].xcom_pull(task_ids="scavenge_supplies"))
    log.info("Evaluating whether supplies are sufficient to justify radio use.")

    if supply_count <= SUPPLY_CRITICAL_THRESHOLD:
        log.error(
            "Supply count %s is at/below critical threshold %s — "
            "conserving radio battery, skipping check-in.",
            supply_count,
            SUPPLY_CRITICAL_THRESHOLD,
        )
        return False

    log.info(
        "Supply count %s is above critical threshold %s — radio check-in approved.",
        supply_count,
        SUPPLY_CRITICAL_THRESHOLD,
    )
    return True


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
default_args = {
    "owner": "bunker_ops",
    "retries": 1,
}

with DAG(
    dag_id="zombie_survival_dag",
    description="Recurring survival routine: scan, scavenge, fight-or-hide, report, radio check-in.",
    # Changed schedule_interval to schedule for Airflow 3.0 compatibility
    schedule="0 6,18 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["zombie-survival", "assignment"],
) as dag:

    # 1. PythonOperator — perimeter scan, produces the threat_level XCom.
    dawn_perimeter_scan_task = PythonOperator(
        task_id="dawn_perimeter_scan",
        python_callable=dawn_perimeter_scan,
    )

    # 2. BashOperator — scavenging run. We simulate a supply count with
    #    bash's $RANDOM and push it to XCom using the do_xcom_push
    #    mechanism (BashOperator pushes stdout's last line automatically
    #    when do_xcom_push=True, so we make the last line the number).
    scavenge_supplies_task = BashOperator(
        task_id="scavenge_supplies",
        bash_command=(
            'echo "Heading out to scavenge nearby stores for supplies." >&2; '
            "SUPPLY_COUNT=$(( RANDOM % 10 )); "
            'echo "Scavenging run complete. Found supply units: $SUPPLY_COUNT" >&2; '
            "echo $SUPPLY_COUNT"
        ),
        do_xcom_push=True,
    )

    # BashOperator's auto-pushed XCom lands under the default key
    # 'return_value' — downstream tasks pull it with a plain
    # xcom_pull(task_ids="scavenge_supplies"), no relabeling task needed.

    # 3. BranchPythonOperator — the fight-or-hide fork.
    decide_fight_or_hide_task = BranchPythonOperator(
        task_id="decide_fight_or_hide",
        python_callable=decide_fight_or_hide,
    )

    # 4a. PythonOperator — only runs if threat_level is high.
    fight_zombies_task = PythonOperator(
        task_id="fight_zombies",
        python_callable=fight_zombies,
    )

    # 4b. BashOperator — only runs if threat_level is low.
    barricade_base_task = BashOperator(
        task_id="barricade_base",
        bash_command=(
            'echo "Threat level acceptable. Reinforcing barricades instead of engaging." >&2; '
            'echo "Barricade reinforcement complete." >&2'
        ),
    )

    # 5. PythonOperator — rejoin point. trigger_rule lets it run even
    #    though exactly one of its two upstream tasks was skipped.
    headcount_report_task = PythonOperator(
        task_id="headcount_report",
        python_callable=headcount_report,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # 6. ShortCircuitOperator — second, independent skip mechanism.
    check_supplies_sufficient_task = ShortCircuitOperator(
        task_id="check_supplies_sufficient",
        python_callable=supplies_are_sufficient,
    )

    # 7. BashOperator — final task, skipped whenever the ShortCircuit
    #    above returns False.
    radio_checkin_task = BashOperator(
        task_id="radio_checkin",
        bash_command=(
            'echo "Broadcasting status to nearby survivor groups on the emergency channel." >&2; '
            'echo "Radio check-in complete." >&2'
        ),
    )

    # ------------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------------
    [dawn_perimeter_scan_task, scavenge_supplies_task] >> decide_fight_or_hide_task
    decide_fight_or_hide_task >> [fight_zombies_task, barricade_base_task]
    [fight_zombies_task, barricade_base_task] >> headcount_report_task

    headcount_report_task >> check_supplies_sufficient_task >> radio_checkin_task
