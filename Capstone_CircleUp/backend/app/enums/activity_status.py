import enum


class ActivityStatus(str, enum.Enum):
    OPEN = "OPEN"
    FULL = "FULL"
    CANCELLED = "CANCELLED"
