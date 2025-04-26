from typing import Optional
from pydantic import BaseModel


class ClientsCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ClientsDB(BaseModel):

    id: int
    name: str
    description: Optional[str] = None
