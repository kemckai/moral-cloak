"""Euthyna: an inspectable record of every evaluation.

Athens required office-holders to submit to an audit at the end of their
term. This log is the small version of that. Each call to
:meth:`moral_cloak.Evaluator.evaluate` appends one record, and the whole
log exports as JSON.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4
import json

from .verdicts import Evaluation


class AuditLog:
    """An ordered list of evaluation records.

    Records are plain dictionaries so a caller can serialize them without
    holding the original objects. ``record`` returns the entry it stored.
    """

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def record(self, evaluation: Evaluation) -> dict[str, Any]:
        entry = {
            "id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evaluation": evaluation.to_dict(),
        }
        self.records.append(entry)
        return entry

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.records, indent=indent, ensure_ascii=False)

    def export(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.records)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self.records[index]
