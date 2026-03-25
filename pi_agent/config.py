import os
from pathlib import Path

SERVER_URL = os.getenv("SERVER_URL", "http://192.168.1.242:8000")
DEVICE_ID = os.getenv("DEVICE_ID", "3149f497-2514-4ffa-80ad-14719c7b808c")
WORK_DIR = Path(os.getenv("WORK_DIR", "./captures"))
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "15"))
WS_CONNECT_TIMEOUT = int(os.getenv("WS_CONNECT_TIMEOUT", "20"))

# Live stream settings
RTMP_HOST = os.getenv("RTMP_HOST", "192.168.1.242")
RTMP_PORT = int(os.getenv("RTMP_PORT", "1935"))
RTMP_APP = os.getenv("RTMP_APP", "live")
LIVE_WIDTH = int(os.getenv("LIVE_WIDTH", "1280"))
LIVE_HEIGHT = int(os.getenv("LIVE_HEIGHT", "720"))
LIVE_FPS = int(os.getenv("LIVE_FPS", "24"))
LIVE_BITRATE = os.getenv("LIVE_BITRATE", "2000k")

WORK_DIR.mkdir(parents=True, exist_ok=True)

WS_URL = SERVER_URL.replace("http://", "ws://").replace("https://", "wss://")
WS_URL = f"{WS_URL}/devices/{DEVICE_ID}/ws"
UPLOAD_URL = f"{SERVER_URL}/devices/{DEVICE_ID}/upload"