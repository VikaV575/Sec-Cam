from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.state import devices


client = TestClient(app)


def test_send_record_command_to_existing_device():
    device_id = "camera-123"

    devices[device_id] = {
        "id": device_id,
        "name": "Living Room Camera",
        "last_seen": None,
    }

    with patch(
        "backend.app.routers.devices.ws_manager.push_command",
        new_callable=AsyncMock,
    ) as mock_push_command:
        response = client.post(
            f"/devices/{device_id}/command",
            json={
                "type": "record",
                "seconds": 10,
            },
        )

    assert response.status_code == 200

    assert response.json() == {
        "ok": True,
        "message": "Command queued for online device",
    }

    mock_push_command.assert_awaited_once_with(
        device_id,
        {
            "type": "record",
            "seconds": 10,
        },
    )

    devices.pop(device_id, None)