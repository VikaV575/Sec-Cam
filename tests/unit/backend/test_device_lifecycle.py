from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
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


def test_create_device_persists_and_returns_new_device():
    with (
        patch("backend.app.routers.devices.uuid.uuid4", return_value="device-fixed-id"),
        patch("backend.app.routers.devices.save_devices") as mock_save_devices,
    ):
        response = client.post("/devices", json={"name": "Backyard Cam"})

    assert response.status_code == 200
    assert response.json() == {
        "id": "device-fixed-id",
        "name": "Backyard Cam",
        "last_seen": None,
        "media": [],
        "commands": [],
    }
    assert devices["device-fixed-id"] == response.json()
    mock_save_devices.assert_called_once()


def test_remove_device_disconnects_and_saves_state():
    device_id = "to-remove"
    devices[device_id] = {"id": device_id, "name": "Garage", "last_seen": None}

    with (
        patch(
            "backend.app.routers.devices.ws_manager.disconnect",
            new_callable=AsyncMock,
        ) as mock_disconnect,
        patch("backend.app.routers.devices.save_devices") as mock_save_devices,
    ):
        response = client.delete(f"/devices/{device_id}/remove")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "message": f"Device {device_id} removed"}
    assert device_id not in devices
    mock_disconnect.assert_awaited_once_with(device_id)
    mock_save_devices.assert_called_once()


def test_command_returns_409_when_device_is_offline():
    device_id = "offline-device"
    devices[device_id] = {"id": device_id, "name": "Patio", "last_seen": None}

    with (
        patch("backend.app.core.activity.uuid.uuid4", return_value="offline-command-id"),
        patch("backend.app.routers.devices.save_devices"),
        patch(
            "backend.app.routers.devices.ws_manager.push_command",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=409, detail="Device is offline"),
        ),
    ):
        response = client.post(
            f"/devices/{device_id}/command",
            json={"type": "record", "seconds": 4},
        )

    assert response.status_code == 409
    assert response.json() == {"detail": "Device is offline"}

    command = devices[device_id]["commands"][0]
    assert command["id"] == "offline-command-id"
    assert command["status"] == "failed"
    assert command["error"] == "Device is offline"


def test_get_live_info_returns_stream_urls():
    device_id = "live-info-1"
    devices[device_id] = {"id": device_id, "name": "Door", "last_seen": None}

    response = client.get(f"/devices/{device_id}/live")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["device_id"] == device_id
    assert payload["live"]["stream_key"] == device_id
    assert payload["live"]["webrtc_url"].endswith(f"/live/{device_id}")
    assert payload["live"]["hls_url"].endswith(f"/live/{device_id}/index.m3u8")
