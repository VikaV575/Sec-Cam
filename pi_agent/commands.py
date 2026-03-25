import aiohttp

try:
    from .config import DEVICE_ID
    from .live import start_live_stream, stop_live_stream
    from .media import capture_snapshot, capture_video, upload_file
    from .state import AgentState
    from .utils import get_live_meta, send_json_safe
except ImportError:
    from config import DEVICE_ID
    from live import start_live_stream, stop_live_stream
    from media import capture_snapshot, capture_video, upload_file
    from state import AgentState
    from utils import get_live_meta, send_json_safe


async def handle_command(
    state: AgentState,
    ws,
    session: aiohttp.ClientSession,
    command: dict,
) -> None:
    cmd_type = command.get("type")
    print(f"[command] received: {command}")

    try:
        await send_json_safe(
            ws,
            {
                "type": "status",
                "status": "started",
                "command": command,
            },
        )

        if cmd_type == "snapshot":
            path = await capture_snapshot()
            await upload_file(session, path)

        elif cmd_type == "record":
            seconds = int(command.get("seconds", 5))
            path = await capture_video(seconds)
            await upload_file(session, path)

        elif cmd_type == "start_live":
            stream_key = str(command.get("stream_key") or DEVICE_ID)
            await start_live_stream(state, stream_key)

        elif cmd_type == "stop_live":
            await stop_live_stream(state)

        else:
            raise ValueError(f"Unsupported command type: {cmd_type}")

        await send_json_safe(
            ws,
            {
                "type": "status",
                "status": "done",
                "command": command,
                "meta": {
                    "live": get_live_meta(state),
                },
            },
        )

    except Exception as e:
        print(f"[command] error: {e}")
        await send_json_safe(
            ws,
            {
                "type": "status",
                "status": "error",
                "command": command,
                "error": str(e),
                "meta": {
                    "live": get_live_meta(state),
                },
            },
        )