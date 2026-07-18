# Sec-Cam

A Raspberry Pi smart security camera platform with a Python device agent, FastAPI backend, React dashboard, WebSocket command delivery, and live streaming through MediaMTX.

## Features

- Raspberry Pi agent with automatic WebSocket reconnection and heartbeats
- Remote snapshot and video recording commands
- Media upload and HTTP file serving
- Device registration and online/offline tracking
- Live-stream start/stop control
- RTMP streaming from the Pi to MediaMTX
- Browser playback through WebRTC
- Unit and integration tests for the agent, backend, WebSockets, uploads, and UI

## Architecture

```text
React dashboard
    │ REST
    ▼
FastAPI backend ───── serves uploaded media
    │ WebSocket
    ▼
Raspberry Pi agent
    │ RTMP
    ▼
MediaMTX
    │ WebRTC / HLS
    ▼
Browser live viewer
```

The backend is the control plane. Live video is sent directly from the Raspberry Pi to MediaMTX rather than passing through FastAPI.

## Project Structure

```text
backend/        FastAPI server, REST routes, WebSocket handling and storage
frontend/       React dashboard
pi_agent/       Raspberry Pi camera and communication agent
tests/          Python integration/unit tests and Vitest UI tests
uploads/        Uploaded snapshots and recordings
docker-compose.yml
mediamtx.yml
```

## Challenges Solved

Some of the engineering challenges explored in this project include:

- keeping a remote device connected reliably
- distinguishing online vs offline state
- sending commands asynchronously
- handling media uploads from an edge device
- integrating live camera streaming into the browser
- structuring a project across frontend / backend / device layers
  
## Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/devices` | Create a device |
| `GET` | `/devices` | List devices and connection status |
| `DELETE` | `/devices/{device_id}/remove` | Remove a device |
| `POST` | `/devices/{device_id}/command` | Send snapshot or recording commands |
| `POST` | `/devices/{device_id}/upload` | Upload captured media |
| `WS` | `/devices/{device_id}/ws` | Device command and heartbeat channel |
| `GET` | `/devices/{device_id}/live` | Get live-stream metadata |
| `POST` | `/devices/{device_id}/live/start` | Start live streaming |
| `POST` | `/devices/{device_id}/live/stop` | Stop live streaming |

## Run Locally

### Docker services

```bash
docker compose up --build
```

- Dashboard: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

Create a device:

```bash
curl -X POST http://localhost:8000/devices \
  -H "Content-Type: application/json" \
  -d '{"name":"Living Room Camera"}'
```

Save the returned `id`; the Raspberry Pi agent uses it as `DEVICE_ID`.

## Run the Raspberry Pi Agent

The Pi requires `rpicam-still`, `rpicam-vid`, and `ffmpeg`.

```bash
cd raspberry-pi-security-camera
python3 -m pip install -r pi_agent/requirements.txt

export SERVER_URL=http://<SERVER_IP>:8000
export DEVICE_ID=<DEVICE_ID>
export RTMP_HOST=<SERVER_IP>

python3 pi_agent/main.py
```

Optional live-stream settings:

```bash
export LIVE_WIDTH=1280
export LIVE_HEIGHT=720
export LIVE_FPS=24
export LIVE_BITRATE=2000k
```

## Commands

Snapshot:

```json
{"type":"snapshot"}
```

Record a clip:

```json
{"type":"record","seconds":10}
```

The backend queues the command, delivers it over WebSocket, and the agent captures and uploads the resulting file.

## Tests

Install Python test dependencies:

```bash
python3 -m pip install pytest pytest-asyncio httpx
```

Run all Python tests:

```bash
python3 -m pytest tests -v
```

Run frontend tests:

```bash
npm --prefix frontend install
npm --prefix frontend run test:run
```

Run both suites:

```bash
python3 -m pytest tests -v && npm --prefix frontend run test:run
```

The tests cover command handling, heartbeats, device lifecycle, offline failures, media uploads, REST-to-WebSocket delivery, live controls, and React UI workflows.

## Current Limitations

- Devices are currently registered through the API rather than the dashboard.
- Uploaded files are served by the backend, but media history and automatic last-upload links are not yet connected to the UI.
- Authentication, cloud deployment, alerts, and computer-vision features are future work.

## Screenshots

<img width="2134" height="1468" alt="Sec-Cam dashboard" src="https://github.com/user-attachments/assets/7799f1f4-f046-402c-873a-e4e9a48758cc" />

<img width="991" height="777" alt="Sec-Cam device view" src="https://github.com/user-attachments/assets/c3a2a0bd-8e73-4b36-b044-47d5256dc265" />
