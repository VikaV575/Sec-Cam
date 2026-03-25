from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
from datetime import datetime

from ..core.config import UPLOAD_DIR, ISRAEL_TZ
from ..core.state import devices
from ..core.storage import save_devices
from ..schemas.device import DeviceCreate
from ..schemas.command import CommandCreate
from ..services.device_ws_manager import ws_manager

router = APIRouter(prefix="/devices", tags=["devices"])


def build_live_info(device_id: str) -> dict:
    stream_key = device_id
    return {
        "stream_key": stream_key,
        "webrtc_url": f"http://YOUR_MEDIAMTX_HOST:8889/live/{stream_key}",
        "hls_url": f"http://YOUR_MEDIAMTX_HOST:8888/live/{stream_key}/index.m3u8",
    }


@router.post("")
def create_device(device: DeviceCreate):
    device_id = str(uuid.uuid4())
    devices[device_id] = {
        "id": device_id,
        "name": device.name,
        "last_seen": None,
    }
    save_devices()
    return devices[device_id]


@router.delete("/{device_id}/remove")
def remove_device(device_id: str):
    removed_device = devices.pop(device_id, None)
    if removed_device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    ws_manager.disconnect(device_id)
    save_devices()
    return {"ok": True, "message": f"Device {device_id} removed"}


@router.post("/{device_id}/upload")
async def upload_file(device_id: str, file: UploadFile = File(...)):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")

    name = devices[device_id]["name"]
    ts = datetime.now(ISRAEL_TZ).strftime("%Y%m%d_%H%M")
    safe_name = file.filename or "file.bin"
    filename = f"{name}_{ts}_{safe_name}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    return {"ok": True, "saved_to": path}


@router.get("")
async def list_devices():
    result = []

    for device in devices.values():
        device_copy = device.copy()
        device_copy["online"] = await ws_manager.is_connected(device["id"])
        result.append(device_copy)

    return result


@router.post("/{device_id}/command")
async def send_command(device_id: str, command: CommandCreate):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")

    cmd = command.model_dump()
    await ws_manager.push_command(device_id, cmd)

    return {"ok": True, "message": "Command queued for online device"}


@router.get("/{device_id}/live")
async def get_live_info(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "ok": True,
        "device_id": device_id,
        "live": build_live_info(device_id),
    }


@router.post("/{device_id}/live/start")
async def start_live(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")

    command = {
        "type": "start_live",
        "stream_key": device_id,
    }

    await ws_manager.push_command(device_id, command)

    return {
        "ok": True,
        "message": "Live start command sent",
        "device_id": device_id,
        "live": build_live_info(device_id),
    }


@router.post("/{device_id}/live/stop")
async def stop_live(device_id: str):
    if device_id not in devices:
        raise HTTPException(status_code=404, detail="Device not found")

    command = {
        "type": "stop_live",
    }

    await ws_manager.push_command(device_id, command)

    return {
        "ok": True,
        "message": "Live stop command sent",
        "device_id": device_id,
    }