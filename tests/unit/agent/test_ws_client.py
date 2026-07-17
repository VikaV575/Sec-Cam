import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pi_agent.state import AgentState
from pi_agent.ws_client import heartbeat_loop, receiver_loop


class FakeWebSocketIterator:
    def __init__(self, messages):
        self.messages = list(messages)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.messages:
            raise StopAsyncIteration
        return self.messages.pop(0)


@pytest.mark.asyncio
async def test_receiver_loop_dispatches_valid_command():
    state = MagicMock(spec=AgentState)
    session = AsyncMock()
    ws = FakeWebSocketIterator([json.dumps({"type": "command", "command": {"type": "snapshot"}})])

    with patch("pi_agent.ws_client.handle_command", new_callable=AsyncMock) as mock_handle_command:
        await receiver_loop(state, ws, session)

    mock_handle_command.assert_awaited_once_with(
        state,
        ws,
        session,
        {"type": "snapshot"},
    )


@pytest.mark.asyncio
async def test_receiver_loop_ignores_non_json_and_continues():
    state = MagicMock(spec=AgentState)
    session = AsyncMock()
    ws = FakeWebSocketIterator(
        [
            "not-json",
            json.dumps({"type": "command", "command": {"type": "record", "seconds": 3}}),
        ]
    )

    with patch("pi_agent.ws_client.handle_command", new_callable=AsyncMock) as mock_handle_command:
        await receiver_loop(state, ws, session)

    mock_handle_command.assert_awaited_once_with(
        state,
        ws,
        session,
        {"type": "record", "seconds": 3},
    )


@pytest.mark.asyncio
async def test_receiver_loop_ignores_invalid_command_payload():
    state = MagicMock(spec=AgentState)
    session = AsyncMock()
    ws = FakeWebSocketIterator(
        [
            json.dumps({"type": "command", "command": "invalid"}),
            json.dumps({"type": "heartbeat"}),
        ]
    )

    with patch("pi_agent.ws_client.handle_command", new_callable=AsyncMock) as mock_handle_command:
        await receiver_loop(state, ws, session)

    mock_handle_command.assert_not_awaited()


@pytest.mark.asyncio
async def test_heartbeat_loop_sends_heartbeat_payload():
    state = MagicMock(spec=AgentState)
    ws = AsyncMock()

    with (
        patch("pi_agent.ws_client.send_json_safe", new_callable=AsyncMock) as mock_send_json_safe,
        patch("pi_agent.ws_client.get_device_meta", return_value={"device_id": "dev-1"}),
        patch(
            "pi_agent.ws_client.asyncio.sleep",
            new_callable=AsyncMock,
            side_effect=asyncio.CancelledError,
        ),
    ):
        with pytest.raises(asyncio.CancelledError):
            await heartbeat_loop(state, ws)

    assert mock_send_json_safe.await_count == 1
    # get the payload from the first await call in a way that works with AsyncMock
    first_await = mock_send_json_safe.await_args_list[0]
    sent_payload = first_await.args[1]
    assert sent_payload["type"] == "heartbeat"
    assert isinstance(sent_payload["ts"], float)
    assert sent_payload["meta"] == {"device_id": "dev-1"}
