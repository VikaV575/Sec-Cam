from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.core.state import devices
from backend.app.main import app
from backend.app.services.device_ws_manager import ws_manager


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_shared_state():
    devices.clear()
    ws_manager.ws_by_device.clear()
    ws_manager.queue_by_device.clear()
    yield
    devices.clear()
    ws_manager.ws_by_device.clear()
    ws_manager.queue_by_device.clear()


def test_delete_media_removes_file_and_metadata(tmp_path):
    media_file = tmp_path / "capture.jpg"
    media_file.write_bytes(b"image")
    devices["camera-1"] = {
        "id": "camera-1",
        "name": "Camera",
        "last_seen": None,
        "commands": [],
        "media": [
            {
                "id": "media-1",
                "filename": media_file.name,
                "url": "/uploads/capture.jpg",
                "media_type": "image",
            }
        ],
    }

    with patch("backend.app.routers.devices.UPLOAD_DIR", str(tmp_path)), patch(
        "backend.app.routers.devices.save_devices"
    ):
        response = client.delete("/devices/camera-1/media/media-1")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert media_file.exists() is False
    assert devices["camera-1"]["media"] == []


def test_delete_media_cleans_metadata_when_file_is_already_missing(tmp_path):
    devices["camera-1"] = {
        "id": "camera-1",
        "name": "Camera",
        "last_seen": None,
        "commands": [],
        "media": [{"id": "media-1", "filename": "missing.jpg"}],
    }

    with patch("backend.app.routers.devices.UPLOAD_DIR", str(tmp_path)), patch(
        "backend.app.routers.devices.save_devices"
    ):
        response = client.delete("/devices/camera-1/media/media-1")

    assert response.status_code == 200
    assert response.json()["file_deleted"] is False
    assert devices["camera-1"]["media"] == []


def test_list_devices_prunes_missing_media_files(tmp_path):
    existing = tmp_path / "existing.jpg"
    existing.write_bytes(b"image")
    devices["camera-1"] = {
        "id": "camera-1",
        "name": "Camera",
        "last_seen": None,
        "commands": [],
        "media": [
            {"id": "existing", "filename": existing.name},
            {"id": "missing", "filename": "missing.jpg"},
        ],
    }

    with patch("backend.app.routers.devices.UPLOAD_DIR", str(tmp_path)), patch(
        "backend.app.routers.devices.save_devices"
    ), patch(
        "backend.app.routers.devices.ws_manager.is_connected",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = client.get("/devices")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()[0]["media"]] == ["existing"]
    assert [item["id"] for item in devices["camera-1"]["media"]] == ["existing"]
