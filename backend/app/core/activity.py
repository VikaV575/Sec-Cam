import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


MAX_MEDIA_ITEMS = 24
MAX_COMMAND_ITEMS = 20

STATUS_MAP = {
    "started": "running",
    "done": "completed",
    "error": "failed",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_activity(device: dict) -> dict:
    if not isinstance(device.get("media"), list):
        device["media"] = []
    if not isinstance(device.get("commands"), list):
        device["commands"] = []
    return device


def add_command(device: dict, command: dict) -> tuple[dict, dict]:
    ensure_activity(device)

    now = utc_now_iso()
    command_id = str(uuid.uuid4())
    payload = {**command, "id": command_id}
    record = {
        **payload,
        "status": "queued",
        "created_at": now,
        "updated_at": now,
        "error": None,
    }

    device["commands"].insert(0, record)
    del device["commands"][MAX_COMMAND_ITEMS:]
    return payload, record


def update_command_status(
    device: dict,
    command_id: str,
    agent_status: str,
    error: str | None = None,
    meta: dict | None = None,
) -> dict | None:
    ensure_activity(device)

    for record in device["commands"]:
        if record.get("id") != command_id:
            continue

        record["status"] = STATUS_MAP.get(agent_status, agent_status)
        record["updated_at"] = utc_now_iso()
        record["error"] = error
        if meta is not None:
            record["meta"] = meta
        return record

    return None


def _media_type(filename: str, content_type: str | None) -> tuple[str, str]:
    guessed_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

    if guessed_type.startswith("image/"):
        return "image", guessed_type
    if guessed_type.startswith("video/"):
        return "video", guessed_type
    return "file", guessed_type


def media_path(upload_dir: str, filename: str) -> Path:
    """Return a path inside upload_dir, ignoring any directory parts in filename."""
    return Path(upload_dir) / Path(filename).name


def add_media(
    device: dict,
    filename: str,
    content_type: str | None,
    size_bytes: int,
) -> dict:
    ensure_activity(device)

    media_type, resolved_content_type = _media_type(filename, content_type)
    item = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "url": f"/uploads/{quote(filename)}",
        "media_type": media_type,
        "content_type": resolved_content_type,
        "size_bytes": size_bytes,
        "uploaded_at": utc_now_iso(),
    }

    device["media"].insert(0, item)
    del device["media"][MAX_MEDIA_ITEMS:]
    return item


def pop_media(device: dict, media_id: str) -> dict | None:
    ensure_activity(device)

    for index, item in enumerate(device["media"]):
        if item.get("id") == media_id:
            return device["media"].pop(index)

    return None


def prune_missing_media(device: dict, upload_dir: str) -> list[dict]:
    """Remove media metadata whose local file no longer exists."""
    ensure_activity(device)

    existing = []
    removed = []

    for item in device["media"]:
        filename = item.get("filename")
        if filename and media_path(upload_dir, filename).is_file():
            existing.append(item)
        else:
            removed.append(item)

    if removed:
        device["media"] = existing

    return removed
