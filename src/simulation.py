from .controller import TransferCaseController
from .models import ControllerInputs, RequestedMode, Signal


def healthy_inputs(now_ms: int, feedback: float = 40.0) -> ControllerInputs:
    return ControllerInputs(
        Signal(1200.0, now_ms),
        Signal(1210.0, now_ms),
        Signal(RequestedMode.AUTO.value, now_ms),
        Signal(feedback, now_ms),
        Signal(1, now_ms),
    )


def main() -> None:
    controller = TransferCaseController()
    for cycle in range(3):
        now = cycle * 100
        print(now, controller.update(now, healthy_inputs(now)))

    now = 400
    inputs = healthy_inputs(now)
    inputs.speed_sensor_b = Signal(1900.0, now)
    print(now, controller.update(now, inputs))

    print("\nFault history:")
    for fault in controller.logger.records:
        print(fault)


if __name__ == "__main__":
    main()
