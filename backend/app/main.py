from fastapi import FastAPI
import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import UPLOAD_DIR
from .core.state import devices
from .core.storage import load_devices
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

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
def startup_event():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    loaded = load_devices()
    devices.update(loaded)

    print(f"Loaded {len(devices)} devices.")


@app.get("/")
def root():
    return {"message": "Backend is alive"}


app.include_router(devices_router)
app.include_router(device_ws_router)