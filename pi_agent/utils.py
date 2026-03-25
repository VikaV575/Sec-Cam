import json
import socket
import time

try:
    from .config import DEVICE_ID, RTMP_APP, RTMP_HOST, RTMP_PORT
except ImportError:
    from config import DEVICE_ID, RTMP_APP, RTMP_HOST, RTMP_PORT


def ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


async def send_json_safe(ws, payload: dict) -> None:
    await ws.send(json.dumps(payload))


def get_live_meta(state) -> dict:
    is_running = state.live_process is not None and state.live_process.returncode is None

    return {
        "running": is_running,
        "stream_key": state.live_stream_key,
        "started_at": state.live_started_at,
        "rtmp_host": RTMP_HOST,
        "rtmp_port": RTMP_PORT,
        "rtmp_app": RTMP_APP,
    }


def get_device_meta(state) -> dict:
    return {
        "hostname": socket.gethostname(),
        "device_id": DEVICE_ID,
        "live": get_live_meta(state),
    }