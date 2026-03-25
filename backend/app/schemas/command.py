from pydantic import BaseModel

class CommandCreate(BaseModel):
    type: str
    seconds: int | None = None