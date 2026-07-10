from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class FaultRecord:
    timestamp_ms: int
    code: str
    severity: str
    description: str


class FaultLogger:
    def __init__(self) -> None:
        self._records: list[FaultRecord] = []
        self._active_codes: set[str] = set()

    def report(self, timestamp_ms: int, code: str, severity: str, description: str) -> None:
        if code not in self._active_codes:
            self._records.append(FaultRecord(timestamp_ms, code, severity, description))
        self._active_codes.add(code)

    def clear_active(self) -> None:
        self._active_codes.clear()

    @property
    def active_codes(self) -> tuple[str, ...]:
        return tuple(sorted(self._active_codes))

    @property
    def records(self) -> tuple[FaultRecord, ...]:
        return tuple(self._records)

    def as_dicts(self) -> list[dict]:
        return [asdict(record) for record in self._records]
