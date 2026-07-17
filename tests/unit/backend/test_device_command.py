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
    
    
    
def test_send_command_to_missing_device_returns_404():
    missing_device_id = "does-not-exist"

    devices.pop(missing_device_id, None)

    with patch(
        "backend.app.routers.devices.ws_manager.push_command",
        new_callable=AsyncMock,
    ) as mock_push_command:
        response = client.post(
            f"/devices/{missing_device_id}/command",
            json={
                "type": "record",
                "seconds": 10,
            },
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Device not found",
    }

    mock_push_command.assert_not_awaited()
    
    
def test_command_without_type_returns_422():
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
            json={"seconds": 10},
        )

    assert response.status_code == 422

    error_details = response.json()["detail"]
    assert error_details[0]["loc"] == ["body", "type"]
    assert error_details[0]["type"] == "missing"

    mock_push_command.assert_not_awaited()

    devices.pop(device_id, None)