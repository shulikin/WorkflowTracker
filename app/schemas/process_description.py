from typing import Optional
from pydantic import BaseModel


class ProcessDescriptionCreate(BaseModel):
    name: str
    position_id: int
    description: Optional[str] = None


class ProcessDescriptionDB(BaseModel):

    id: int
    name: str
    description: Optional[str] = None
