from pydantic import BaseModel

class DeviceCreate(BaseModel):
    name: str