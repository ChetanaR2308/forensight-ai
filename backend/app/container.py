from app.repositories.mongo import MongoRepository
from app.services.audit import AuditService
from app.services.correlation import TimelineService
from app.services.integrations import (
    DeterministicWorkflowOrchestrator,
    InMemoryGraphStore,
    InMemoryVectorStore,
)
from app.services.processing import ProcessingPipeline
from app.services.query import DeterministicQueryService
from app.services.reporting import ReportService
from app.services.storage import LocalObjectStorage


class ServiceContainer:
    def __init__(self) -> None:
        self.repository = MongoRepository()
        self.storage = LocalObjectStorage()
        self.pipeline = ProcessingPipeline()
        self.timeline = TimelineService()
        self.query = DeterministicQueryService()
        self.reporting = ReportService()
        self.graph = InMemoryGraphStore()
        self.vector = InMemoryVectorStore()
        self.workflow = DeterministicWorkflowOrchestrator()
        self.audit = AuditService(self.repository)


_container: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container
