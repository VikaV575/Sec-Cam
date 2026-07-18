from fastapi import FastAPI
import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.activity import ensure_activity, trim_command_history
from .core.config import UPLOAD_DIR
from .core.state import devices
from .core.storage import load_devices, save_devices
from .routers.devices import router as devices_router
from .routers.device_ws import router as device_ws_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads",
)


@app.on_event("startup")
def startup_event():
    loaded = load_devices()
    devices.clear()
    devices.update(loaded)

    command_history_changed = False
    for device in devices.values():
        ensure_activity(device)
        if trim_command_history(device):
            command_history_changed = True

    if command_history_changed:
        save_devices()

    print(f"Loaded {len(devices)} devices.")


@app.get("/")
def root():
    return {"message": "Backend is alive"}


app.include_router(devices_router)
app.include_router(device_ws_router)
