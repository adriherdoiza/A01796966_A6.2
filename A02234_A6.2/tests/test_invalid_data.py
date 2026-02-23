import tempfile
import unittest
from pathlib import Path

from src.storage import JsonStorage


class TestInvalidData(unittest.TestCase):
    def test_invalid_json_structure_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fpath = Path(tmp) / "bad.json"
            fpath.write_text('{ "not": "a list" }', encoding="utf-8")
            store = JsonStorage(str(fpath))
            data = store.load_list()
            self.assertEqual(data, [])
