from __future__ import annotations

from dataclasses import dataclass

from .fault_logger import FaultLogger
from .models import ControllerInputs, ControllerOutput, ControllerState, RequestedMode


@dataclass(frozen=True)
class SafetyConfig:
    max_speed_rpm: float = 8000.0
    sensor_disagreement_rpm: float = 150.0
    signal_timeout_ms: int = 250
    can_timeout_ms: int = 500
    actuator_tolerance_pct: float = 12.0
    actuator_fault_persistence_cycles: int = 3


class TransferCaseController:
    """Simplified transfer-case controller with safety monitoring."""

    def __init__(self, config: SafetyConfig | None = None) -> None:
        self.config = config or SafetyConfig()
        self.state = ControllerState.INIT
        self.logger = FaultLogger()
        self._actuator_mismatch_cycles = 0
        self._safe_latched = False

    def reset(self) -> None:
        self.state = ControllerState.INIT
        self.logger.clear_active()
        self._actuator_mismatch_cycles = 0
        self._safe_latched = False

    def update(self, now_ms: int, inputs: ControllerInputs) -> ControllerOutput:
        self.logger.clear_active()

        if self._safe_latched:
            self.state = ControllerState.SAFE
            return self._output(0.0)

        sensor_fault = self._check_speed_sensors(now_ms, inputs)
        mode_fault = self._check_requested_mode(now_ms, inputs)
        can_fault = self._check_can(now_ms, inputs)
        desired_command = self._calculate_command(inputs)
        actuator_fault = self._check_actuator(now_ms, desired_command, inputs)

        if actuator_fault or can_fault:
            self.state = ControllerState.SAFE
            self._safe_latched = True
            return self._output(0.0)

        if sensor_fault or mode_fault:
            self.state = ControllerState.DEGRADED
            return self._output(0.0)

        self.state = ControllerState.NORMAL
        return self._output(desired_command)

    def _check_speed_sensors(self, now_ms: int, inputs: ControllerInputs) -> bool:
        a = inputs.speed_sensor_a
        b = inputs.speed_sensor_b
        fault = False

        for name, signal in (("A", a), ("B", b)):
            if not signal.valid or now_ms - signal.timestamp_ms > self.config.signal_timeout_ms:
                self.logger.report(now_ms, f"SPD_{name}_TIMEOUT", "MEDIUM",
                                   f"Speed sensor {name} is invalid or timed out.")
                fault = True
                continue

            try:
                value = float(signal.value)
            except (TypeError, ValueError):
                self.logger.report(now_ms, f"SPD_{name}_TYPE", "MEDIUM",
                                   f"Speed sensor {name} contains a non-numeric value.")
                fault = True
                continue

            if not 0.0 <= value <= self.config.max_speed_rpm:
                self.logger.report(now_ms, f"SPD_{name}_RANGE", "MEDIUM",
                                   f"Speed sensor {name} is outside the valid range.")
                fault = True

        if not fault and abs(float(a.value) - float(b.value)) > self.config.sensor_disagreement_rpm:
            self.logger.report(now_ms, "SPD_DISAGREE", "MEDIUM",
                               "Redundant speed sensors disagree beyond the threshold.")
            fault = True

        return fault

    def _check_requested_mode(self, now_ms: int, inputs: ControllerInputs) -> bool:
        signal = inputs.requested_mode
        if not signal.valid or now_ms - signal.timestamp_ms > self.config.signal_timeout_ms:
            self.logger.report(now_ms, "MODE_TIMEOUT", "MEDIUM",
                               "Requested mode is invalid or timed out.")
            return True
        try:
            RequestedMode(str(signal.value))
        except ValueError:
            self.logger.report(now_ms, "MODE_INVALID", "MEDIUM",
                               "Requested operating mode is unsupported.")
            return True
        return False

    def _check_can(self, now_ms: int, inputs: ControllerInputs) -> bool:
        heartbeat = inputs.can_heartbeat
        if not heartbeat.valid or now_ms - heartbeat.timestamp_ms > self.config.can_timeout_ms:
            self.logger.report(now_ms, "CAN_TIMEOUT", "HIGH",
                               "CAN-like heartbeat is missing or timed out.")
            return True
        return False

    def _calculate_command(self, inputs: ControllerInputs) -> float:
        try:
            mode = RequestedMode(str(inputs.requested_mode.value))
        except ValueError:
            return 0.0
        return {
            RequestedMode.TWO_WHEEL_DRIVE: 0.0,
            RequestedMode.AUTO: 40.0,
            RequestedMode.FOUR_WHEEL_DRIVE: 100.0,
        }[mode]

    def _check_actuator(self, now_ms: int, command_pct: float,
                        inputs: ControllerInputs) -> bool:
        feedback = inputs.actuator_feedback_pct

        if not feedback.valid or now_ms - feedback.timestamp_ms > self.config.signal_timeout_ms:
            self.logger.report(now_ms, "ACT_FEEDBACK_TIMEOUT", "HIGH",
                               "Actuator feedback is invalid or timed out.")
            return True

        try:
            value = float(feedback.value)
        except (TypeError, ValueError):
            self.logger.report(now_ms, "ACT_FEEDBACK_TYPE", "HIGH",
                               "Actuator feedback is non-numeric.")
            return True

        if not 0.0 <= value <= 100.0:
            self.logger.report(now_ms, "ACT_FEEDBACK_RANGE", "HIGH",
                               "Actuator feedback is outside the valid range.")
            return True

        if abs(command_pct - value) > self.config.actuator_tolerance_pct:
            self._actuator_mismatch_cycles += 1
        else:
            self._actuator_mismatch_cycles = 0

        if self._actuator_mismatch_cycles >= self.config.actuator_fault_persistence_cycles:
            self.logger.report(now_ms, "ACT_MISMATCH", "HIGH",
                               "Actuator feedback does not match the command.")
            return True
        return False

    def _output(self, command_pct: float) -> ControllerOutput:
        return ControllerOutput(self.state, command_pct, self.logger.active_codes)
