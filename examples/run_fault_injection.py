import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.controller import TransferCaseController
from src.models import ControllerInputs, RequestedMode, Signal


def base_inputs(now_ms: int, feedback: float = 40.0) -> ControllerInputs:
    return ControllerInputs(
        Signal(1500.0, now_ms),
        Signal(1510.0, now_ms),
        Signal(RequestedMode.AUTO.value, now_ms),
        Signal(feedback, now_ms),
        Signal(1, now_ms),
    )


def show(name, output):
    print(f"\n{name}\n{'-' * len(name)}")
    print("State:", output.state.value)
    print("Command:", output.actuator_command_pct)
    print("Faults:", ", ".join(output.active_faults) or "None")


def main():
    c = TransferCaseController()
    show("TC-01 Healthy operation", c.update(100, base_inputs(100)))

    c = TransferCaseController()
    x = base_inputs(1000)
    x.speed_sensor_a = Signal(1500.0, 600)
    show("TC-02 Frozen sensor", c.update(1000, x))

    c = TransferCaseController()
    x = base_inputs(100)
    x.speed_sensor_a = Signal(12000.0, 100)
    show("TC-03 Implausible value", c.update(100, x))

    c = TransferCaseController()
    x = base_inputs(1000)
    x.can_heartbeat = Signal(1, 0)
    show("TC-04 Missing CAN heartbeat", c.update(1000, x))

    c = TransferCaseController()
    for i in range(3):
        now = i * 100
        out = c.update(now, base_inputs(now, feedback=0.0))
    show("TC-05 Actuator mismatch", out)

    c = TransferCaseController()
    x = base_inputs(100)
    x.requested_mode = Signal("INVALID_MODE", 100)
    show("TC-06 Corrupted mode", c.update(100, x))


if __name__ == "__main__":
    main()
