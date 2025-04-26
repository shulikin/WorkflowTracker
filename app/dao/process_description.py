from app.dao.base import BaseDAO  # путь к твоему BaseDAO
from app.models.models import ProcessDescription


class ProcessDescriptionDAO(BaseDAO[ProcessDescription]):
    model = ProcessDescription
