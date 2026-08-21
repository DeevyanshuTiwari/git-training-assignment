# Zombie Survival DAG — Assignment README

## Table of Contents
1. [The Story](#the-story)
2. [Task Flow & Design Reasoning](#task-flow--design-reasoning)
3. [Requirements Checklist](#requirements-checklist)
4. [XCom Usage](#xcom-usage)
5. [Skip Logic](#skip-logic)
6. [Scheduling](#scheduling)
7. [Logging](#logging)
8. [Airflow Variables](#airflow-variables)
9. [Setup & Deployment](#setup--deployment)
10. [Triggering via the REST API](#triggering-via-the-rest-api)
11. [Troubleshooting Log](#troubleshooting-log-issues-actually-hit)
12. [Deliverables Checklist](#deliverables-checklist)

---

## The Story

Every dawn and dusk, the bunker's automated survival routine runs itself so
no human has to remember an eight-step checklist. It scans the perimeter
for threats, sends someone to scavenge supplies, decides whether today is
a fight day or a hide day based on that scan, takes a headcount, and —
battery permitting — checks in with other survivor groups over the radio.

## Task Flow & Design Reasoning

```
dawn_perimeter_scan ─┐
                      ├─► decide_fight_or_hide ─┬─► fight_zombies   ─┐
scavenge_supplies ────┘                          └─► barricade_base ─┤
                                                                      ▼
                                                          headcount_report
                                                                      │
                                                                      ▼
                                                     check_supplies_sufficient
                                                                      │
                                                                      ▼
                                                              radio_checkin
```

| # | Task ID | Operator | Purpose |
|---|---|---|---|
| 1 | `dawn_perimeter_scan` | PythonOperator | Generates a `threat_level` (0–10), pushes it to XCom |
| 2 | `scavenge_supplies` | BashOperator | Generates a `supply_count` (0–9), auto-pushed to XCom |
| 3 | `decide_fight_or_hide` | BranchPythonOperator | Reads `threat_level`, branches the DAG |
| 4a | `fight_zombies` | PythonOperator | Runs only on the "fight" branch |
| 4b | `barricade_base` | BashOperator | Runs only on the "hide" branch |
| 5 | `headcount_report` | PythonOperator | Rejoins the branch, logs a run summary |
| 6 | `check_supplies_sufficient` | ShortCircuitOperator | Gates the final task on supply level |
| 7 | `radio_checkin` | BashOperator | Skipped when supplies are critical |

**Why this shape:** the DAG mirrors a real decision loop — assess, react,
report, communicate — rather than a flat checklist. Two *independent*
branch points (not just one) demonstrate that a "skip" can come from
different mechanisms for different reasons, not just one code path
copy-pasted twice.

Tasks 1 and 2 run in parallel since scanning the perimeter and scavenging
for supplies don't depend on each other's results.

## Requirements Checklist

| Requirement | How it's met |
|---|---|
| 6–8 tasks total | 7 tasks |
| Both PythonOperator and BashOperator | 3 PythonOperator, 1 BranchPythonOperator, 1 ShortCircuitOperator, 3 BashOperator |
| XCom between at least two tasks | `threat_level` and `supply_count`, each read by 2+ downstream tasks |
| At least one deliberate skip | Two independent skip mechanisms (branch + ShortCircuit) |
| Non-generic cron schedule | `0 6,18 * * *` — dawn patrol and dusk lockdown |
| Meaningful logs, every level, task logger (not print) | `logging.getLogger("airflow.task")`, debug through critical |
| Clean, PEP8 code | Type-hinted, docstringed, constants pulled from Variables |
| Triggered via Airflow REST API | See [Triggering via the REST API](#triggering-via-the-rest-api) |

## XCom Usage

- **`threat_level`** — pushed explicitly by `dawn_perimeter_scan` via
  `context["ti"].xcom_push(key="threat_level", value=...)`. Pulled by
  `decide_fight_or_hide` (drives the branch decision) and
  `headcount_report` (for the summary log). This is the value that
  actually changes control flow, not just something logged for show.
- **`supply_count`** — auto-pushed by `scavenge_supplies`
  (`BashOperator(do_xcom_push=True)`, which pushes the last line of
  stdout). Pulled by `headcount_report` and `check_supplies_sufficient`.

## Skip Logic

Two independent conditions, using two different Airflow mechanisms:

1. **BranchPythonOperator** (`decide_fight_or_hide`) — whichever of
   `fight_zombies` / `barricade_base` is *not* returned by the callable
   is automatically marked `skipped` by Airflow.
2. **ShortCircuitOperator** (`check_supplies_sufficient`) — if
   `supply_count <= 3` (the critical threshold), the callable returns
   `False` and `radio_checkin` is skipped, to justify conserving radio
   battery when supplies are low.

`headcount_report` uses `trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS`
so it still runs even though exactly one of its two upstream branch tasks
was skipped — this is what lets the branch rejoin cleanly.

## Scheduling

`0 6,18 * * *` — runs at 06:00 and 18:00 every day (dawn patrol, dusk
lockdown). A survivor group wouldn't reassess constantly or at one
arbitrary hour a day — they'd check in at the two natural inflection
points where visibility and risk change the most.

## Logging

Every task logs through `logging.getLogger("airflow.task")` (never bare
`print`), so entries show up in Airflow's per-task log viewer. All five
levels are used deliberately:

- `debug` — routine internal detail (e.g. "beginning perimeter sweep")
- `info` — normal expected outcomes (scan results, branch chosen)
- `warning` — elevated-but-handled situations (high threat level)
- `error` — a task deciding to skip downstream work (critical supplies)
- `critical` — active combat engagement

Reading the logs of any run reconstructs exactly what happened and why
anything was skipped.

## Airflow Variables

Set under **Admin → Variables** (or the DAG runs on sensible defaults if
you skip this):

- `zombie_threat_threshold` (default `6`) — threat level at/above which
  the DAG fights instead of hiding.
- `zombie_supply_critical_threshold` (default `3`) — supply count at/below
  which the radio check-in is skipped.

## Setup & Deployment

```bash
mkdir zombie-airflow && cd zombie-airflow
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker compose up airflow-init
docker compose up -d
```

Copy `zombie_survival_dag.py` into `zombie-airflow/dags/`. Airflow polls
that folder automatically. Open `http://localhost:8080` (default login
`airflow` / `airflow`), find `zombie_survival_dag` in the DAG list, and
**unpause it** (DAGs start paused by default).

Optionally set the two Variables above under Admin → Variables.

## Triggering via the REST API

This project runs **Airflow 3**, which changed the API path and auth
model from the older, more commonly-documented Airflow 2 flow.

**1. Get a bearer token** (Airflow 3 does not accept Basic Auth directly
on API calls — you must exchange credentials for a token first):

```bash
curl -X POST 'http://localhost:8080/auth/token' \
  -H 'Content-Type: application/json' \
  -d '{"username": "airflow", "password": "airflow"}'
```

Copy the `access_token` value from the response.

**2. Trigger the DAG run:**

- Method: `POST`
- URL: `http://localhost:8080/api/v2/dags/zombie_survival_dag/dagRuns`
  (note **`/api/v2/`**, not `/api/v1/` — v1 is the Airflow 2 path)
- Authorization: Bearer Token → paste the `access_token`
- Body (raw, JSON) — `logical_date` is a **required** field in Airflow 3:
  ```json
  {"logical_date": null}
  ```
- Send

A successful response returns `200` with a body containing `dag_run_id`
and `"state": "queued"`. **Screenshot this request + response panel** —
it's a required deliverable.

Equally doable through the Swagger UI at `http://localhost:8080/api/v2/ui/`
(click Authorize, paste the token, find `POST /dags/{dag_id}/dagRuns`,
Try it out, fill in `dag_id` and the same body, Execute).

## Troubleshooting Log (issues actually hit)

Documented here since they're version-specific gotchas worth knowing:

1. **`AttributeError: 'RuntimeTaskInstance' object has no attribute 'log'`**
   — In Airflow 3's Task SDK, `context["ti"]` no longer exposes a `.log`
   attribute (an Airflow 2-ism). Fixed by using a standard logger via
   `logging.getLogger("airflow.task")` instead — this is the
   version-safe pattern going forward.
2. **`401 Not authenticated` on the dagRuns endpoint with Basic Auth** —
   Airflow 3's REST API only accepts Bearer tokens, obtained from
   `POST /auth/token`. Basic Auth credentials in Postman's Authorization
   tab don't work directly against `/api/v2/`.
3. **`422 Unprocessable Content — "logical_date": "Field required"`** —
   Airflow 3 requires `logical_date` explicitly in the POST body (it was
   optional in Airflow 2's `/api/v1/`). Passing `{"logical_date": null}`
   runs the DAG immediately.

## Deliverables Checklist

- [x] `zombie_survival_dag.py` — well-commented, PEP8-compliant
- [ ] Screenshot: DAG graph view with a completed run, skipped task visible
- [ ] Screenshot: API trigger request + response (Postman/Swagger)
- [x] `README.md` (this file)
