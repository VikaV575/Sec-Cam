# Sec-Cam

Sec-Cam is a Raspberry Pi–based smart security camera platform with a Python device agent, FastAPI control server, React dashboard, and browser live streaming through MediaMTX.

The project demonstrates an end-to-end edge-device architecture involving REST APIs, WebSockets, asynchronous command delivery, media capture and upload, device presence tracking, and a browser-based control interface.

## Current Capabilities

### Raspberry Pi agent

- Connects to the backend through a persistent WebSocket.
- Sends periodic heartbeat messages.
- Receives and executes remote commands.
- Captures JPEG snapshots with `rpicam-still`.
- Records MP4 video clips with `rpicam-vid`.
- Uploads captured media to the backend using multipart HTTP requests.
- Starts and stops an RTMP live-streaming pipeline using `rpicam-vid` and `ffmpeg`.
- Reconnects to the backend with increasing retry delays after connection failures.
- Cleans up an active live-stream process when the agent shuts down.

### FastAPI backend

- Creates, lists, and removes registered devices.
- Persists the device registry in `devices_db.json`.
- Tracks device connection state and `last_seen` timestamps.
- Accepts media uploads and serves the `uploads/` directory over HTTP.
- Validates command request bodies with Pydantic.
- Rejects commands for missing or offline devices.
- Queues remote commands and delivers them to connected devices through WebSockets.
- Provides endpoints for starting, stopping, and retrieving live-stream metadata.

### React frontend

- Displays registered devices and their online/offline state.
- Refreshes device information periodically and on demand.
- Sends snapshot and video-recording commands.
- Allows the recording duration to be selected.
- Starts and stops live mode.
- Embeds the MediaMTX WebRTC viewer in the dashboard.
- Contains support for rendering a media link when an upload URL is supplied.

### Automated tests

The repository contains Python and frontend tests covering:

- agent command handling and error reporting;
- default recording behavior;
- agent WebSocket message parsing and heartbeat generation;
- device creation and removal;
- offline and missing-device failures;
- media upload and file persistence;
- device online-status reporting;
- live start/stop API behavior;
- REST-to-WebSocket command delivery;
- WebSocket connection, heartbeat, and disconnection flows;
- React device controls, live-view behavior, empty states, and API utilities.

## Architecture

```text
                         control plane

React dashboard ──REST──> FastAPI backend
                              │
                              │ queued commands over WebSocket
                              ▼
                       Raspberry Pi agent

                          media plane

Raspberry Pi camera
        │
        ├── snapshot / recording ──HTTP upload──> FastAPI `/uploads`
        │
        └── H.264 + ffmpeg ──RTMP──> MediaMTX ──WebRTC──> Browser
```

The backend coordinates devices and commands, but it does not relay the live video stream. Live video is sent directly from the Raspberry Pi to MediaMTX and viewed by the browser through WebRTC.

## Main System Flows

### Device setup and connection

1. A device record is created through `POST /devices`.
2. The returned device ID is configured on the Raspberry Pi.
3. The agent connects to `WS /devices/{device_id}/ws`.
4. The backend accepts the connection only if the device ID is registered.
5. Connection and heartbeat messages update the device's `last_seen` value.

### Remote snapshot or recording

1. The browser sends a command to `POST /devices/{device_id}/command`.
2. The backend verifies that the device exists and is currently connected.
3. The command is placed in the device's asynchronous queue.
4. The backend WebSocket sends the command to the Raspberry Pi agent.
5. The agent captures the requested media.
6. The agent uploads the file to `POST /devices/{device_id}/upload`.
7. The backend saves the file under `uploads/`.

### Live streaming

1. The browser calls `POST /devices/{device_id}/live/start`.
2. The backend sends a `start_live` command through the device WebSocket.
3. The agent launches a `rpicam-vid` and `ffmpeg` pipeline.
4. The stream is published to MediaMTX over RTMP.
5. The browser opens the corresponding MediaMTX WebRTC viewer.
6. Calling `POST /devices/{device_id}/live/stop` terminates the live process.

## Technology Stack

### Device agent

- Python
- `aiohttp`
- `websockets`
- Raspberry Pi camera tools (`rpicam-still`, `rpicam-vid`)
- `ffmpeg`

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- WebSockets
- JSON file persistence

### Frontend

- React 19
- Vite
- JavaScript
- Vitest
- React Testing Library

### Streaming and local infrastructure

- MediaMTX
- RTMP ingest
- WebRTC and HLS output
- Docker Compose

## Repository Structure

```text
raspberry-pi-security-camera/
├── README.md
├── docker-compose.yml
├── mediamtx.yml
├── devices_db.json             # Local runtime data; not tracked by Git
├── uploads/                    # Uploaded snapshots and recordings
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/               # Configuration, shared state, JSON storage
│       ├── routers/            # REST and device WebSocket routes
│       ├── schemas/            # Pydantic request models
│       └── services/           # WebSocket connection and command queues
│
├── frontend/
│   ├── dockerfile
│   ├── package.json
│   ├── vitest.config.js
│   └── src/
│       ├── App.jsx
│       ├── components/
│       └── utils/
│
├── pi_agent/
│   ├── main.py
│   ├── config.py
│   ├── state.py
│   ├── commands.py
│   ├── media.py
│   ├── live.py
│   ├── ws_client.py
│   ├── utils.py
│   └── requirements.txt
│
└── tests/
    ├── unit/
    │   ├── agent/
    │   ├── backend/
    │   └── frontend/
    └── integration/
        └── backend/
```

## Backend API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Backend health response |
| `POST` | `/devices` | Create a device from a JSON body containing `name` |
| `GET` | `/devices` | List devices with their current WebSocket connection status |
| `DELETE` | `/devices/{device_id}/remove` | Remove a device and disconnect it |
| `POST` | `/devices/{device_id}/command` | Queue a command for an online device |
| `POST` | `/devices/{device_id}/upload` | Upload a media file using multipart form data |
| `GET` | `/devices/{device_id}/live` | Return live-stream metadata for a device |
| `POST` | `/devices/{device_id}/live/start` | Send the live-start command |
| `POST` | `/devices/{device_id}/live/stop` | Send the live-stop command |
| `WS` | `/devices/{device_id}/ws` | Device command and heartbeat channel |
| `GET` | `/uploads/{filename}` | Retrieve a saved upload |

Example generic commands:

```json
{"type": "snapshot", "seconds": null}
```

```json
{"type": "record", "seconds": 10}
```

## Running the Local Services

### Prerequisites

- Docker and Docker Compose
- A local network connection between the development computer and Raspberry Pi for device testing

The database file is intentionally not tracked. Create the local runtime files before starting Docker Compose:

```bash
printf '{}\n' > devices_db.json
mkdir -p uploads
```

Start the backend, frontend, and MediaMTX services:

```bash
docker compose up --build
```

Open:

- React dashboard: `http://localhost:5173`
- FastAPI backend: `http://localhost:8000`
- FastAPI interactive API documentation: `http://localhost:8000/docs`
- MediaMTX WebRTC HTTP server: `http://localhost:8889`

The frontend uses `http://localhost:8000` by default. A different API address can be supplied through `VITE_API_URL`.

## Registering a Device

Device registration is currently performed through the backend API rather than through the React dashboard.

```bash
curl -X POST http://localhost:8000/devices \
  -H 'Content-Type: application/json' \
  -d '{"name":"Front Door Camera"}'
```

The response contains the generated device ID:

```json
{
  "id": "generated-device-id",
  "name": "Front Door Camera",
  "last_seen": null
}
```

Use this exact ID when configuring the Raspberry Pi agent.

## Running the Raspberry Pi Agent

### Raspberry Pi prerequisites

- Raspberry Pi OS with the camera enabled
- A supported Raspberry Pi camera
- Python 3
- `rpicam-still` and `rpicam-vid`
- `ffmpeg`

Install the agent's Python dependencies:

```bash
python3 -m pip install -r pi_agent/requirements.txt
```

Configure the agent. `SERVER_URL` and `RTMP_HOST` must point to the computer running the backend and MediaMTX, using an address reachable from the Raspberry Pi rather than `localhost`.

```bash
export SERVER_URL=http://<HOST_LAN_IP>:8000
export DEVICE_ID=<REGISTERED_DEVICE_ID>
export RTMP_HOST=<HOST_LAN_IP>
```

Optional settings include:

```bash
export WORK_DIR=./captures
export HEARTBEAT_INTERVAL=15
export WS_CONNECT_TIMEOUT=20
export RTMP_PORT=1935
export RTMP_APP=live
export LIVE_WIDTH=1280
export LIVE_HEIGHT=720
export LIVE_FPS=24
export LIVE_BITRATE=2000k
```

Run the agent from the repository root:

```bash
python3 pi_agent/main.py
```

The live sender is part of the main agent; no separate `webrtc_sender.py` process is used.

## Running the Tests

Install the Python test dependencies together with the backend and agent dependencies:

```bash
python3 -m pip install \
  -r backend/requirements.txt \
  -r pi_agent/requirements.txt \
  pytest pytest-asyncio httpx
```

Install the frontend dependencies:

```bash
npm --prefix frontend install
```

Run all Python unit and integration tests:

```bash
python3 -m pytest tests -v
```

Run only the Python unit tests:

```bash
python3 -m pytest tests/unit -v
```

Run only the Python integration tests:

```bash
python3 -m pytest tests/integration -v
```

Run the frontend tests once:

```bash
npm --prefix frontend run test:run
```

Run both Python and frontend test suites:

```bash
python3 -m pytest tests -v && npm --prefix frontend run test:run
```

For frontend watch mode:

```bash
npm --prefix frontend test
```

## Current Limitations

- Device registration and removal are available through the API but are not yet exposed as dashboard controls.
- Device data is persisted in a JSON file rather than a production database.
- WebSocket connections and outgoing command queues are stored in memory.
- Authentication, authorization, and multi-user support are not implemented.
- Uploaded files are served by the backend, but upload history and automatic last-upload links are not yet connected to the dashboard.
- Status messages returned by the agent are logged by the backend but are not yet surfaced as command progress or failure notifications in the UI.
- The live viewer assumes MediaMTX is reachable on the browser's current hostname at port `8889`.
- Snapshot, recording, and live-stream commands require Raspberry Pi camera tools and cannot perform real capture without the target hardware.

## Reliability and Validation Work

The project includes several reliability-oriented behaviors and tests:

- commands for offline devices return a clear conflict response;
- unknown devices are rejected by both REST and WebSocket routes;
- malformed WebSocket messages are ignored without stopping the receiver loop;
- agent commands emit started, completed, or error status messages;
- failed camera and upload operations propagate error details;
- live processes are prevented from starting twice;
- live process state is reset when the process exits;
- shutdown cleanup stops active live processes;
- automated tests reset shared backend and WebSocket state between scenarios;
- integration tests validate command delivery across REST, backend queues, and WebSockets.

## Planned Improvements

- Connect uploaded-media metadata and history to the dashboard.
- Surface agent command progress and failures in the UI.
- Add a dashboard flow for registering and removing devices.
- Add persistent media metadata storage.
- Add authentication and multiple-user support.
- Add CI to run the Python and frontend tests automatically.
- Add motion detection, event-triggered recording, and object detection.
- Improve stream startup feedback, quality controls, and deployment configuration.

## Screenshots

<img width="2134" height="1468" alt="Sec-Cam dashboard" src="https://github.com/user-attachments/assets/7799f1f4-f046-402c-873a-e4e9a48758cc" />

<img width="991" height="777" alt="Sec-Cam live view" src="https://github.com/user-attachments/assets/c3a2a0bd-8e73-4b36-b044-47d5256dc265" />

## Author

Built as a personal full-stack, IoT, networking, and software-testing project.