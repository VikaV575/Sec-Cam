import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..core.state import devices
from ..core.storage import save_devices
from ..services.device_ws_manager import ws_manager

router = APIRouter(prefix="/devices", tags=["device-ws"])


@router.websocket("/{device_id}/ws")
async def device_ws(device_id: str, websocket: WebSocket):
    if device_id not in devices:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(device_id, websocket)

    devices[device_id]["last_seen"] = datetime.now(timezone.utc).isoformat()
    save_devices()

    q = await ws_manager.get_queue(device_id)

    async def sender_loop():
        while True:
            print("waiting for command...")
            cmd = await q.get()
            print("got command from queue:", cmd)

            payload = {"type": "command", "command": cmd}
            print("about to send:", payload)

            try:
                await websocket.send_json(payload)
                print("send_json finished")
            except Exception as e:
                print("send_json error:", repr(e))
                raise

    async def receiver_loop():
        while True:
            msg = await websocket.receive_json()
            print("[ws from device]", device_id, msg)
            devices[device_id]["last_seen"] = datetime.now(timezone.utc).isoformat()
            save_devices()

    try:
        await asyncio.gather(sender_loop(), receiver_loop())
    except WebSocketDisconnect:
        print("WebSocketDisconnect")
        await ws_manager.disconnect(device_id)
    except Exception as e:
        print("WS route exception:", repr(e))
        await ws_manager.disconnect(device_id)
        try:
            await websocket.close()
        except Exception:
            pass