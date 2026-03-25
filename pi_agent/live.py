import asyncio
import shlex
import time

try:
    from .config import LIVE_BITRATE, LIVE_FPS, LIVE_HEIGHT, LIVE_WIDTH, RTMP_APP, RTMP_HOST, RTMP_PORT
    from .state import AgentState
except ImportError:
    from config import LIVE_BITRATE, LIVE_FPS, LIVE_HEIGHT, LIVE_WIDTH, RTMP_APP, RTMP_HOST, RTMP_PORT
    from state import AgentState


def build_rtmp_url(stream_key: str) -> str:
    return f"rtmp://{RTMP_HOST}:{RTMP_PORT}/{RTMP_APP}/{stream_key}"


async def monitor_live_process(state: AgentState, proc: asyncio.subprocess.Process) -> None:
    stdout_task = asyncio.create_task(proc.stdout.read()) if proc.stdout else None
    stderr_task = asyncio.create_task(proc.stderr.read()) if proc.stderr else None

    returncode = await proc.wait()

    stdout_text = ""
    stderr_text = ""

    if stdout_task:
        stdout = await stdout_task
        stdout_text = stdout.decode(errors="ignore")
    if stderr_task:
        stderr = await stderr_task
        stderr_text = stderr.decode(errors="ignore")

    print(f"[live] process exited with code {returncode}")

    if stdout_text.strip():
        print(f"[live stdout] {stdout_text}")
    if stderr_text.strip():
        print(f"[live stderr] {stderr_text}")

    async with state.live_lock:
        if state.live_process is proc:
            state.live_process = None
            state.live_stream_key = None
            state.live_started_at = None


async def start_live_stream(state: AgentState, stream_key: str) -> None:
    async with state.live_lock:
        if state.live_process is not None and state.live_process.returncode is None:
            raise RuntimeError("Live stream is already running")

        if not stream_key:
            raise ValueError("Missing stream_key")

        rtmp_url = build_rtmp_url(stream_key)

        command = (
            "bash -lc "
            + shlex.quote(
                "set -o pipefail && "
                f"rpicam-vid "
                f"-n "
                f"-t 0 "
                f"--inline "
                f"--width {LIVE_WIDTH} "
                f"--height {LIVE_HEIGHT} "
                f"--framerate {LIVE_FPS} "
                f"--bitrate {LIVE_BITRATE.rstrip('k')}000 "
                f"--codec h264 "
                f"-o - "
                f"| ffmpeg "
                f"-loglevel warning "
                f"-re "
                f"-fflags nobuffer "
                f"-flags low_delay "
                f"-f h264 "
                f"-i - "
                f"-c:v copy "
                f"-an "
                f"-f flv "
                f"{shlex.quote(rtmp_url)}"
            )
        )

        print(f"[live] starting stream to {rtmp_url}")
        print(f"[live] shell command: {command}")

        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await asyncio.sleep(2)

        if proc.returncode is not None:
            stdout, stderr = await proc.communicate()
            raise RuntimeError(
                f"Live stream exited immediately ({proc.returncode})\n"
                f"stdout: {stdout.decode(errors='ignore')}\n"
                f"stderr: {stderr.decode(errors='ignore')}"
            )

        state.live_process = proc
        state.live_stream_key = stream_key
        state.live_started_at = time.time()

        asyncio.create_task(monitor_live_process(state, proc))


async def stop_live_stream(state: AgentState) -> None:
    async with state.live_lock:
        proc = state.live_process
        if proc is None or proc.returncode is not None:
            state.live_process = None
            state.live_stream_key = None
            state.live_started_at = None
            return

        print("[live] stopping stream...")
        proc.terminate()

    try:
        await asyncio.wait_for(proc.wait(), timeout=5)
    except asyncio.TimeoutError:
        print("[live] terminate timeout; killing process")
        proc.kill()
        await proc.wait()

    async with state.live_lock:
        if state.live_process is proc:
            state.live_process = None
            state.live_stream_key = None
            state.live_started_at = None

    print("[live] stopped")