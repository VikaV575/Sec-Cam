from backend.app.core.activity import add_command, add_media, ensure_activity, update_command_status


def test_add_command_creates_trackable_queued_record():
    device = {"id": "device-1", "name": "Camera"}

    payload, record = add_command(device, {"type": "record", "seconds": 4})

    assert payload["id"] == record["id"]
    assert payload["type"] == "record"
    assert record["status"] == "queued"
    assert device["commands"][0] == record


def test_update_command_status_maps_agent_values():
    device = {"commands": [], "media": []}
    _, record = add_command(device, {"type": "snapshot"})

    updated = update_command_status(device, record["id"], "started")
    assert updated["status"] == "running"

    updated = update_command_status(device, record["id"], "done", meta={"live": False})
    assert updated["status"] == "completed"
    assert updated["meta"] == {"live": False}


def test_update_command_status_stores_agent_error():
    device = {"commands": [], "media": []}
    _, record = add_command(device, {"type": "snapshot"})

    updated = update_command_status(device, record["id"], "error", error="camera unavailable")

    assert updated["status"] == "failed"
    assert updated["error"] == "camera unavailable"


def test_add_media_builds_ui_metadata():
    device = {}

    media = add_media(
        device,
        filename="front_camera_snapshot.jpg",
        content_type="image/jpeg",
        size_bytes=1234,
    )

    assert media["media_type"] == "image"
    assert media["url"] == "/uploads/front_camera_snapshot.jpg"
    assert media["size_bytes"] == 1234
    assert device["media"][0] == media


def test_ensure_activity_upgrades_existing_devices():
    device = {"id": "legacy-device"}

    ensure_activity(device)

    assert device["media"] == []
    assert device["commands"] == []
