<img width="2134" height="1468" alt="image" src="https://github.com/user-attachments/assets/baae6c08-4485-4c9c-a20c-8889c88806a0" /><img width="1067" height="734" alt="Screenshot 2026-03-25 at 12 23 22" src="https://github.com/user-attachments/assets/2dde0975-3e1a-42b7-bfeb-1f1e3294b9e5" /># Sec-Cam

A Raspberry Pi–based smart security camera system with a FastAPI backend, React dashboard, WebSocket-based device control, and live video streaming through a dedicated media server.

## Overview

**Sec-Cam** is a distributed IoT security camera project built around a Raspberry Pi camera device and a web dashboard.

The system allows a remote user to:
- register and monitor camera devices
- request **snapshots**
- record and upload **video clips**
- view device **online/offline status**
- send commands in real time using **WebSockets**
- start and stop **live video streaming**
- view live camera output in the browser using **WebRTC**

This project was built to simulate a real-world edge device + backend + frontend architecture, with room for future computer vision features such as event detection and smart alerts.

---

## Features

### Implemented
- Raspberry Pi device agent
- Device registration and heartbeat system
- Online/offline device tracking
- Remote snapshot capture
- Remote video recording and upload
- FastAPI backend API
- React frontend dashboard
- Real-time command delivery via WebSockets
- Browser-based live stream via **WebRTC**
- Dedicated media server for live streaming (**MediaMTX**)
- RTMP ingest pipeline from Raspberry Pi to media server
- Dockerized local development environment

### Planned / Future Work
- Motion detection
- Cat / object detection using computer vision
- Smart event alerts
- Authentication and multi-user support
- Cloud deployment
- Media storage improvements
- Recording history and timeline view
- Stream startup and quality optimizations

---

## Architecture

The project consists of 4 main parts:

### 1. Raspberry Pi Agent
Runs on the Raspberry Pi and is responsible for:
- connecting to the backend
- sending heartbeats
- receiving commands
- capturing images / videos from the Pi camera
- uploading media files
- starting and stopping live streaming on demand

For live streaming, the Pi uses:
- `rpicam-vid` to capture H.264 video from the camera
- `ffmpeg` to package and publish the stream over **RTMP**

### 2. FastAPI Backend
Acts as the **control server** and is responsible for:
- managing devices
- exposing REST API endpoints
- handling uploads
- tracking device status
- delivering commands over WebSockets
- triggering live stream start / stop actions

The backend does **not** carry the video stream itself.  
Instead, it controls the device and provides metadata / URLs used by the frontend.

### 3. Media Server (MediaMTX)
Acts as the **media plane** of the system and is responsible for:
- receiving the live stream from the Raspberry Pi via **RTMP**
- exposing the stream to clients using **WebRTC** / **HLS**
- allowing multiple viewers to watch the same live stream
- serving as the foundation for future recording / replay features

This keeps live video handling separate from the backend API.

### 4. React Frontend
Provides a browser dashboard for:
- viewing registered devices
- checking online status
- requesting snapshots / videos
- viewing uploaded media
- opening and controlling live view

---

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn
- WebSockets
- Pydantic

### Frontend
- React
- Vite
- JavaScript / TypeScript (depending on your setup)

### Device / Edge
- Raspberry Pi Zero 2 W
- Raspberry Pi Camera Module NoIR
- Python
- `rpicam-vid`
- `ffmpeg`

### Media / Streaming
- MediaMTX
- RTMP
- WebRTC
- HLS

### Dev / Infra
- Docker
- Docker Compose

---

## How It Works

### Device Registration
A Raspberry Pi device registers with the backend and receives / uses a unique `device_id`.

### Heartbeats
The Pi agent periodically sends heartbeat messages so the backend knows the device is online.

### Commands
When the user clicks an action in the dashboard (for example, **Take Snapshot** or **Start Live**), the backend sends a command to the device via **WebSocket**.

### Capture + Upload
For snapshots and recordings, the device performs the action locally, saves the media, and uploads the result back to the backend.

### Live View
For live streaming:
1. the frontend requests **Start Live**
2. the backend sends a **start_live** command to the Pi
3. the Pi starts a camera pipeline using `rpicam-vid` + `ffmpeg`
4. the Pi publishes the stream to **MediaMTX** using **RTMP**
5. the browser connects to the stream using **WebRTC**

This architecture allows lower-latency live video while keeping the Raspberry Pi lightweight and the backend focused on device orchestration.

---

## Live Streaming Flow

```text
Browser (React)
    ↓
FastAPI Backend (control plane)
    ↓ WebSocket command
Raspberry Pi Agent
    ↓ RTMP
MediaMTX
    ↓ WebRTC / HLS
Browser Viewer

## Project Structure

```bash
sec-cam/
├── README.md
├── docker-compose.yml
├── mediamtx.yml
├── devices_db.json
│
├── backend/                  # FastAPI backend / control server
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/             # Config, shared state, storage
│       ├── routers/          # REST + WebSocket routes
│       ├── schemas/          # Pydantic models
│       └── services/         # Device / WebSocket services
│
├── frontend/                 # React dashboard
│   ├── dockerfile
│   ├── package.json
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── components/       # UI components (device cards, live view)
│       ├── styles/           # Shared styles
│       └── utils/            # API + time helpers
│
├── pi_agent/                 # Raspberry Pi device agent
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
└── uploads/                  # Captured snapshots / recordings

> Adjust this tree if your actual folders are slightly different.

---

## API / Core Capabilities

Example backend responsibilities include:

- `POST /devices/register` – register a device
- `POST /devices/{device_id}/heartbeat` – update device status
- `POST /devices/{device_id}/commands/snapshot` – request snapshot
- `POST /devices/{device_id}/commands/video` – request video recording
- `POST /devices/{device_id}/upload` – upload captured media
- `WS /devices/{device_id}/ws` – real-time command channel
- `POST /devices/{device_id}/live/start` – start live streaming
- `POST /devices/{device_id}/live/stop` – stop live streaming
- `GET /devices/{device_id}/live` – retrieve stream metadata
- `WS /devices/{device_id}/ws` – real-time device command channel

---

## Running Locally

### Prerequisites
- Docker
- Docker Compose

### Start the backend + frontend
```bash
docker compose up --build
```

Then open:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

---

## Running the Raspberry Pi Agent

On the Raspberry Pi, configure environment variables such as:

```bash
SERVER_URL=http://<YOUR_SERVER_IP>:8000
DEVICE_ID=<YOUR_DEVICE_ID>
```

Then run the agent:

```bash
python agent.py
```

If using the live stream sender as a separate process:

```bash
python webrtc_sender.py
```

> In production, the agent can be configured to run automatically as a system service on boot.

---

## Example Use Flow

1. Start backend and frontend
2. Start the Raspberry Pi agent
3. Open the dashboard in the browser
4. Confirm the device appears **online**
5. Click **Take Snapshot** or **Record Video**
6. View the uploaded media in the dashboard
7. Open **Live View** to stream from the camera

---

## Why This Project Is Interesting

This project is more than a basic CRUD app — it combines:

- **IoT / edge device communication**
- **backend API design**
- **real-time networking**
- **media handling**
- **browser-based live streaming**
- **full-stack integration**

It was designed as a practical systems project that mirrors challenges found in real-world products:
- unreliable device connectivity
- async communication
- media transfer
- low-latency streaming
- service orchestration

---

## Challenges Solved

Some of the engineering challenges explored in this project include:

- keeping a remote device connected reliably
- distinguishing online vs offline state
- sending commands asynchronously
- handling media uploads from an edge device
- integrating live camera streaming into the browser
- structuring a project across frontend / backend / device layers

---

## Future Improvements

Potential next steps:
- add authentication and user accounts
- persist device / media data in a database
- deploy to a cloud server
- add object detection or motion-triggered recording
- build notifications / alerting
- improve stream startup time and media quality

---

## Screenshots

<img width="2134" height="1468" alt="image" src="https://github.com/user-attachments/assets/7799f1f4-f046-402c-873a-e4e9a48758cc" />
<img width="991" height="777" alt="Screenshot 2026-03-25 at 12 27 48" src="https://github.com/user-attachments/assets/c3a2a0bd-8e73-4b36-b044-47d5256dc265" />

---

## Author

Built as a personal systems / full-stack / IoT project.
