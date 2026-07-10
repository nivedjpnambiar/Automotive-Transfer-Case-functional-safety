# Transfer-Case Functional Safety Simulation

An educational portfolio project demonstrating an **ISO 26262-oriented** workflow for a simplified electronic transfer-case controller.

> This is not a production safety system and does not claim formal ISO 26262 compliance.

## Demonstrated skills

- Functional Safety concept development
- V-model-oriented development
- Requirements Engineering and traceability
- HARA and FMEA documentation
- State-machine design
- Sensor plausibility, range, and timeout monitoring
- Actuator feedback monitoring
- Safe-state transitions and fault logging
- Fault-injection and automated testing

## Run

```bash
python -m src.simulation
python examples/run_fault_injection.py
python -m unittest discover -s tests -v
```

## System

The controller receives two shaft-speed signals, a requested mode, actuator feedback, and a CAN-like heartbeat. It produces an actuator command and transitions between:

- `INIT`
- `NORMAL`
- `DEGRADED`
- `SAFE`

Critical faults latch the `SAFE` state until reset.

## Structure

```text
transfer_case_functional_safety/
├── README.md
├── src/
├── tests/
├── examples/
└── docs/
```

## **Functional-Safety-Konzept für eine elektronische Verteilergetriebesteuerung – Eigenprojekt**

Entwicklung einer ISO-26262-orientierten Sicherheitsarchitektur mit HARA, FMEA, Safety Goals sowie funktionalen und technischen Sicherheitsanforderungen. Implementierung einer Python-basierten Steuergerät-Simulation mit redundanter Sensorsignalüberwachung, Fehlererkennung, Safe-State-Logik, Fault Injection und rückverfolgbaren Testfällen entlang des V-Modells.
