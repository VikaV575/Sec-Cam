import pytest
from unittest.mock import AsyncMock, MagicMock, call, patch
from pi_agent.state import AgentState
from pi_agent.commands import handle_command

@pytest.mark.asyncio
async def test_record_uses_default_duration():
    state = MagicMock(spec=AgentState)
    ws = AsyncMock()
    session = AsyncMock()
    command = {"type": "record"}

    with (
        patch(
            "pi_agent.commands.capture_video",
            new_callable=AsyncMock,
            return_value="/tmp/video.mp4",
        ) as mock_capture_video,
        patch(
            "pi_agent.commands.upload_file",
            new_callable=AsyncMock,
        ) as mock_upload_file,
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

    mock_capture_video.assert_awaited_once_with(5)

    mock_upload_file.assert_awaited_once_with(
        session,
        "/tmp/video.mp4",
    )

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
                    "status": "done",
                    "command": command,
                    "meta": {
                        "live": {"active": False},
                    },
                },
            ),
        ]
    )