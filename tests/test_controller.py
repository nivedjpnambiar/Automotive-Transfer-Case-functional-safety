import unittest

from src.controller import TransferCaseController
from src.models import ControllerInputs, ControllerState, RequestedMode, Signal


def make_inputs(now_ms: int, feedback: float = 40.0) -> ControllerInputs:
    return ControllerInputs(
        Signal(1000.0, now_ms),
        Signal(1010.0, now_ms),
        Signal(RequestedMode.AUTO.value, now_ms),
        Signal(feedback, now_ms),
        Signal(1, now_ms),
    )


class ControllerTests(unittest.TestCase):
    def test_tc_01_healthy(self):
        out = TransferCaseController().update(100, make_inputs(100))
        self.assertEqual(out.state, ControllerState.NORMAL)
        self.assertEqual(out.actuator_command_pct, 40.0)

    def test_tc_02_disagreement(self):
        c = TransferCaseController()
        x = make_inputs(100)
        x.speed_sensor_b = Signal(1400.0, 100)
        out = c.update(100, x)
        self.assertEqual(out.state, ControllerState.DEGRADED)
        self.assertIn("SPD_DISAGREE", out.active_faults)

    def test_tc_03_timeout(self):
        c = TransferCaseController()
        x = make_inputs(1000)
        x.speed_sensor_a = Signal(1000.0, 600)
        out = c.update(1000, x)
        self.assertEqual(out.state, ControllerState.DEGRADED)
        self.assertIn("SPD_A_TIMEOUT", out.active_faults)

    def test_tc_04_range(self):
        c = TransferCaseController()
        x = make_inputs(100)
        x.speed_sensor_a = Signal(9000.0, 100)
        out = c.update(100, x)
        self.assertEqual(out.state, ControllerState.DEGRADED)
        self.assertIn("SPD_A_RANGE", out.active_faults)

    def test_tc_05_can_timeout(self):
        c = TransferCaseController()
        x = make_inputs(1000)
        x.can_heartbeat = Signal(1, 0)
        out = c.update(1000, x)
        self.assertEqual(out.state, ControllerState.SAFE)
        self.assertIn("CAN_TIMEOUT", out.active_faults)

    def test_tc_06_invalid_mode(self):
        c = TransferCaseController()
        x = make_inputs(100)
        x.requested_mode = Signal("BROKEN", 100)
        out = c.update(100, x)
        self.assertEqual(out.state, ControllerState.DEGRADED)
        self.assertIn("MODE_INVALID", out.active_faults)

    def test_tc_07_actuator_mismatch(self):
        c = TransferCaseController()
        for i in range(3):
            now = i * 100
            out = c.update(now, make_inputs(now, feedback=0.0))
        self.assertEqual(out.state, ControllerState.SAFE)
        self.assertIn("ACT_MISMATCH", out.active_faults)

    def test_tc_08_safe_latched(self):
        c = TransferCaseController()
        x = make_inputs(1000)
        x.can_heartbeat = Signal(1, 0)
        c.update(1000, x)
        out = c.update(1100, make_inputs(1100))
        self.assertEqual(out.state, ControllerState.SAFE)

    def test_tc_09_reset(self):
        c = TransferCaseController()
        x = make_inputs(1000)
        x.can_heartbeat = Signal(1, 0)
        c.update(1000, x)
        c.reset()
        out = c.update(1100, make_inputs(1100))
        self.assertEqual(out.state, ControllerState.NORMAL)


if __name__ == "__main__":
    unittest.main()
