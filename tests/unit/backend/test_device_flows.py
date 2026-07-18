from pathlib import Path
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


def test_websocket_connected_device_receives_remote_command():
    device_id = "camera-live-1"
    command_payload = {"type": "record", "seconds": 8}

    devices[device_id] = {"id": device_id, "name": "Front Door", "last_seen": None}

    with (
        patch("backend.app.core.activity.uuid.uuid4", return_value="command-ws-id"),
        patch("backend.app.routers.device_ws.save_devices"),
        patch("backend.app.routers.devices.save_devices"),
        client.websocket_connect(f"/devices/{device_id}/ws") as websocket,
    ):
        response = client.post(f"/devices/{device_id}/command", json=command_payload)

        assert response.status_code == 200
        response_command = response.json()["command"]
        assert response_command["id"] == "command-ws-id"
        assert response_command["status"] == "queued"

        assert websocket.receive_json() == {
            "type": "command",
            "command": {
                "type": "record",
                "seconds": 8,
                "id": "command-ws-id",
            },
        }


def test_upload_file_saves_media_for_existing_device(tmp_path):
    device_id = "camera-upload-1"
    devices[device_id] = {"id": device_id, "name": "KitchenCam", "last_seen": None}

    with (
        patch("backend.app.routers.devices.UPLOAD_DIR", str(tmp_path)),
        patch("backend.app.routers.devices.save_devices"),
    ):
        response = client.post(
            f"/devices/{device_id}/upload",
            files={"file": ("snapshot.jpg", b"img-bytes", "image/jpeg")},
        )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["ok"] is True
    assert "KitchenCam_" in response_data["saved_to"]
    assert response_data["saved_to"].endswith("_snapshot.jpg")
    assert tmp_path.joinpath(Path(response_data["saved_to"]).name).read_bytes() == b"img-bytes"
    assert response_data["media"]["media_type"] == "image"
    assert response_data["media"]["content_type"] == "image/jpeg"
    assert response_data["media"]["size_bytes"] == len(b"img-bytes")


def test_list_devices_returns_online_status_from_ws_manager():
    devices["camera-1"] = {"id": "camera-1", "name": "Cam 1", "last_seen": None}
    devices["camera-2"] = {"id": "camera-2", "name": "Cam 2", "last_seen": None}

    with patch(
        "backend.app.routers.devices.ws_manager.is_connected",
        new_callable=AsyncMock,
        side_effect=[True, False],
    ):
        response = client.get("/devices")

    assert response.status_code == 200
    payload = {item["id"]: item for item in response.json()}
    assert payload["camera-1"]["online"] is True
    assert payload["camera-2"]["online"] is False
    assert payload["camera-1"]["media"] == []
    assert payload["camera-1"]["commands"] == []


def test_start_live_sends_command_and_returns_stream_metadata():
    device_id = "camera-live-start"
    devices[device_id] = {"id": device_id, "name": "Backyard", "last_seen": None}

    with (
        patch("backend.app.core.activity.uuid.uuid4", return_value="start-live-id"),
        patch("backend.app.routers.devices.save_devices"),
        patch(
            "backend.app.routers.devices.ws_manager.push_command",
            new_callable=AsyncMock,
        ) as mock_push_command,
    ):
        response = client.post(f"/devices/{device_id}/live/start")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["ok"] is True
    assert response_data["device_id"] == device_id
    assert response_data["live"]["stream_key"] == device_id
    assert response_data["live"]["webrtc_url"].endswith(f"/live/{device_id}")
    assert response_data["command"]["id"] == "start-live-id"
    assert response_data["command"]["type"] == "start_live"
    assert response_data["command"]["status"] == "queued"

    mock_push_command.assert_awaited_once_with(
        device_id,
        {
            "type": "start_live",
            "stream_key": device_id,
            "id": "start-live-id",
        },
    )


def test_stop_live_sends_stop_command():
    device_id = "camera-live-stop"
    devices[device_id] = {"id": device_id, "name": "Garage", "last_seen": None}

    with (
        patch("backend.app.core.activity.uuid.uuid4", return_value="stop-live-id"),
        patch("backend.app.routers.devices.save_devices"),
        patch(
            "backend.app.routers.devices.ws_manager.push_command",
            new_callable=AsyncMock,
        ) as mock_push_command,
    ):
        response = client.post(f"/devices/{device_id}/live/stop")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["ok"] is True
    assert response_data["message"] == "Live stop command sent"
    assert response_data["device_id"] == device_id
    assert response_data["command"]["id"] == "stop-live-id"
    assert response_data["command"]["type"] == "stop_live"
    assert response_data["command"]["status"] == "queued"

    mock_push_command.assert_awaited_once_with(
        device_id,
        {
            "type": "stop_live",
            "id": "stop-live-id",
        },
    )
