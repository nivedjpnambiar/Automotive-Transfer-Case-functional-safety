# Safety Concept

## Safety goals
- SG-01: Prevent unintended actuator engagement.
- SG-02: Detect implausible or missing speed information.
- SG-03: Enter a safe state after critical communication or actuator-monitoring faults.

## Safe state
- Actuator command = 0%
- State = SAFE
- Fault latched until reset

## Degraded state
- Actuator command = 0%
- State = DEGRADED
- Recovery allowed after recoverable faults disappear

## Safety mechanisms
Range checks, timestamp checks, redundant-sensor comparison, mode validation, actuator command-feedback comparison, heartbeat monitoring, fault logging, and a safe-state latch.
