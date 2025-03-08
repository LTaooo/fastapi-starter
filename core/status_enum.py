from enum import Enum


class StatusEnum(Enum):
    success = 200
    error = 500
    validate_fail = 422