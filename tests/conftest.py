from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def isolate_test_database(monkeypatch, tmp_path):
    """Prevent tests from reading or writing the real devices_db.json file."""
    test_db = tmp_path / "devices_test_db.json"
    monkeypatch.setattr("backend.app.core.storage.DB_FILE", str(test_db))
