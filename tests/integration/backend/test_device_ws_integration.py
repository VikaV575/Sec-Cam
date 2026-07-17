import time
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

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


def test_ws_rejects_unknown_device():
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/devices/missing-device/ws"):
            pass

    assert exc.value.code == 1008


def test_ws_heartbeat_updates_last_seen_and_disconnects():
    device_id = "integration-heartbeat"
    devices[device_id] = {"id": device_id, "name": "Hallway", "last_seen": None}

    with patch("backend.app.routers.device_ws.save_devices") as mock_save_devices:
        with client.websocket_connect(f"/devices/{device_id}/ws") as websocket:
            assert device_id in ws_manager.ws_by_device

            assert devices[device_id]["last_seen"] is not None

            websocket.send_json({"type": "heartbeat"})
            for _ in range(20):
                if mock_save_devices.call_count >= 2:
                    break
                time.sleep(0.01)
            assert mock_save_devices.call_count >= 2

        for _ in range(20):
            if device_id not in ws_manager.ws_by_device:
                break
            time.sleep(0.01)

    assert device_id not in ws_manager.ws_by_device


def test_ws_connected_device_receives_command_via_rest():
    device_id = "integration-command"
    devices[device_id] = {"id": device_id, "name": "Porch", "last_seen": None}
    command = {"type": "record", "seconds": 6}

    with patch("backend.app.routers.device_ws.save_devices"):
        with client.websocket_connect(f"/devices/{device_id}/ws") as websocket:
            response = client.post(f"/devices/{device_id}/command", json=command)

            assert response.status_code == 200
            assert response.json() == {
                "ok": True,
                "message": "Command queued for online device",
            }
            assert websocket.receive_json() == {
                "type": "command",
                "command": command,
            }
