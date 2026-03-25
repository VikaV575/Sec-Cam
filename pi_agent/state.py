import asyncio
from dataclasses import dataclass
from dataclasses import field
from typing import Optional


@dataclass
class AgentState:
    live_process: Optional[asyncio.subprocess.Process] = None
    live_stream_key: Optional[str] = None
    live_started_at: Optional[float] = None
    live_lock: asyncio.Lock = field(default_factory=asyncio.Lock)