from unittest.mock import AsyncMock, MagicMock, call, patch
import pytest
from pi_agent.commands import handle_command
from pi_agent.state import AgentState


@pytest.mark.asyncio
async def test_unknown_command_sends_error_status():
    state = MagicMock(spec=AgentState)
    ws = AsyncMock()
    session = AsyncMock()
    command = {"type": "invalid_command"}

    with (
        patch(
            "pi_agent.commands.send_json_safe",
            new_callable=AsyncMock,
        ) as mock_send,
        patch(
            "pi_agent.commands.get_live_meta",
            return_value={"active": False},
        ),
    ):
        await handle_command(state, ws, session, command)

    mock_send.assert_has_awaits(
        [
            call(
                ws,
                {
                    "type": "status",
                    "status": "started",
                    "command": command,
                },
            ),
            call(
                ws,
                {
                    "type": "status",
                    "status": "error",
                    "command": command,
                    "error": "Unsupported command type: invalid_command",
                    "meta": {
                        "live": {"active": False},
                    },
                },
            ),
        ]
    )