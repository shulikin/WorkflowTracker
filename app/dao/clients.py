from app.dao.base import BaseDAO  # путь к твоему BaseDAO
from app.models.models import Clients


class ClientsDAO(BaseDAO[Clients]):
    model = Clients
