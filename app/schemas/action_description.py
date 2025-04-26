from typing import Optional
from pydantic import BaseModel


class ActionDescriptionCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ActionDescriptionDB(BaseModel):

    id: int
    name: str
    description: Optional[str] = None
