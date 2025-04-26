from app.dao.base import BaseDAO  # путь к твоему BaseDAO
from app.models.models import ActionDescription


class ActionDescriptionDAO(BaseDAO[ActionDescription]):
    model = ActionDescription
