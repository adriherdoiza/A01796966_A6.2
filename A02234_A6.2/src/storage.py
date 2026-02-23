from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar


T = TypeVar("T")


class JsonStorage:
    """Simple JSON storage with safe loading and error tolerance."""

    def __init__(self, filepath: str) -> None:
        self.path = Path(filepath)

    def load_list(self) -> List[Dict[str, Any]]:
        """Load a list from JSON file. If invalid, print error and return empty."""
        if not self.path.exists():
            return []
        try:
            content = self.path.read_text(encoding="utf-8").strip()
            if not content:
                return []
            data = json.loads(content)
            if not isinstance(data, list):
                print(f"[ERROR] Invalid JSON structure in {self.path} (expected list).")
                return []
            return data
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[ERROR] Could not read {self.path}: {exc}")
            return []

    def save_list(self, items: List[Dict[str, Any]]) -> None:
        """Save list to JSON file safely."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")

    @staticmethod
    def to_dict_list(objects: List[Any]) -> List[Dict[str, Any]]:
        return [asdict(obj) for obj in objects]

    @staticmethod
    def from_dict_list(items: List[Dict[str, Any]], cls: Type[T]) -> List[T]:
        converted: List[T] = []
        for item in items:
            try:
                converted.append(cls(**item))  # type: ignore[arg-type]
            except TypeError as exc:
                print(f"[ERROR] Invalid record for {cls.__name__}: {item} ({exc})")
        return converted
