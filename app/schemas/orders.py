from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderCreate(BaseModel):
    number: int
    description: Optional[str] = None
    client_id: int
    user_id: int


class OrdersDB(BaseModel):

    id: int
    number: int
    description: Optional[str] = None
    client_id: int
    user_id: int
    updated_at: datetime
    created_at: datetime
