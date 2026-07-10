from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ControllerState(str, Enum):
    INIT = "INIT"
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    SAFE = "SAFE"


class RequestedMode(str, Enum):
    TWO_WHEEL_DRIVE = "2WD"
    AUTO = "AUTO"
    FOUR_WHEEL_DRIVE = "4WD"


@dataclass
class Signal:
    value: float | str
    timestamp_ms: int
    valid: bool = True


@dataclass
class ControllerInputs:
    speed_sensor_a: Signal
    speed_sensor_b: Signal
    requested_mode: Signal
    actuator_feedback_pct: Signal
    can_heartbeat: Signal


@dataclass
class ControllerOutput:
    state: ControllerState
    actuator_command_pct: float
    active_faults: tuple[str, ...]
