import asyncio
import json
import time
import aiohttp
import websockets

try:
    from .commands import handle_command
    from .config import HEARTBEAT_INTERVAL, WS_CONNECT_TIMEOUT, WS_URL
    from .state import AgentState
    from .utils import get_device_meta, send_json_safe
except ImportError:
    from commands import handle_command
    from config import HEARTBEAT_INTERVAL, WS_CONNECT_TIMEOUT, WS_URL
    from state import AgentState
    from utils import get_device_meta, send_json_safe


async def heartbeat_loop(state: AgentState, ws) -> None:
    while True:
        await send_json_safe(
            ws,
            {
                "type": "heartbeat",
                "ts": time.time(),
                "meta": get_device_meta(state),
            },
        )
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def receiver_loop(state: AgentState, ws, session: aiohttp.ClientSession) -> None:
    async for raw_msg in ws:
        try:
            msg = json.loads(raw_msg)
        except json.JSONDecodeError:
            print(f"[ws] non-json message: {raw_msg}")
            continue

        print(f"[ws] received: {msg}")

        if msg.get("type") == "command":
            command = msg.get("command")
            if isinstance(command, dict):
                await handle_command(state, ws, session, command)
            else:
                print("[ws] invalid command payload")
        else:
            print(f"[ws] ignoring message type: {msg.get('type')}")


async def connect_forever(state: AgentState) -> None:
    reconnect_delay = 2

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                print(f"[connect] ws url: {WS_URL}")

                async with websockets.connect(
                    WS_URL,
                    open_timeout=WS_CONNECT_TIMEOUT,
                    ping_interval=20,
                    ping_timeout=20,
                    max_size=2 * 1024 * 1024,
                ) as ws:
                    print("[connect] connected")
                    reconnect_delay = 2

                    await send_json_safe(
                        ws,
                        {
                            "type": "hello",
                            "meta": get_device_meta(state),
                        },
                    )

                    await asyncio.gather(
                        heartbeat_loop(state, ws),
                        receiver_loop(state, ws, session),
                    )

            except Exception as e:
                print(f"[connect] disconnected/error: {e}")
                print(f"[connect] reconnecting in {reconnect_delay}s...")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 30)