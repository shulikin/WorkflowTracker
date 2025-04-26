from app.dao.base import BaseDAO  # путь к твоему BaseDAO
from app.models.models import Position


class PositionDAO(BaseDAO[Position]):
    model = Position
