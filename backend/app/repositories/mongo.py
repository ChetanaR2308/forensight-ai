from app.repositories.memory import InMemoryRepository
from app.core.config import settings


class MongoRepository(InMemoryRepository):
    """Replaceable Mongo adapter.

    MVP default behavior uses in-memory fallback unless USE_MONGO=true and pymongo client can connect.
    """

    def __init__(self) -> None:
        super().__init__()
        self._enabled = False
        if settings.use_mongo:
            try:
                from pymongo import MongoClient

                self._client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=1000)
                self._client.admin.command("ping")
                self._db = self._client[settings.mongo_db_name]
                self._enabled = True
            except Exception:
                self._enabled = False
