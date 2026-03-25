import asyncio

try:
    from .config import DEVICE_ID
    from .state import AgentState
    from .ws_client import connect_forever
except ImportError:
    from config import DEVICE_ID
    from state import AgentState
    from ws_client import connect_forever


def main() -> None:
    if DEVICE_ID == "PUT_DEVICE_ID_HERE":
        raise SystemExit("You must set DEVICE_ID env var or edit the script.")

    state = AgentState()
    asyncio.run(connect_forever(state))

if __name__ == "__main__":
    main()