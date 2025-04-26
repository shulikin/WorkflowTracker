from datetime import datetime
from pydantic import BaseModel


class PositionCreate(BaseModel):
    name: str


class PositionDB(BaseModel):
    id: int
    name: str
    updated_at: datetime
    created_at: datetime
