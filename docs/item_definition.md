# Item Definition

## Item
Simplified electronic transfer-case control system.

## Purpose
Control a simulated actuator used to distribute drivetrain torque between front and rear axles.

## Inputs
- Speed Sensor A
- Speed Sensor B
- Requested mode
- Actuator position feedback
- CAN-like heartbeat

## Outputs
- Actuator command, 0–100%
- Controller state
- Diagnostic fault codes

## Scope exclusions
Physical drivetrain mechanics, real CAN, production ECU hardware, RTOS, formal ASIL decomposition, and quantitative hardware metrics.
