from app.container import get_container
from app.services.knowledge_graph import KnowledgeGraphAdapter, NullKnowledgeGraph
from app.services.orchestration import LangGraphInvestigationOrchestrator
from app.services.rag import CaseScopedRetriever


class ServiceContainer:
    def __init__(self) -> None:
        self.repository = None
        self.storage = None
        self.pipeline = None
        self.timeline = None
        self.query = None
        self.reporting = None
        self.graph = None
        self.vector = None
        self.workflow = None
        self.audit = None
        self.knowledge_graph = None
        self.rag = None

        from app.repositories.mongo import MongoRepository
        from app.services.audit import AuditService
        from app.services.correlation import TimelineService
        from app.services.integrations import DeterministicWorkflowOrchestrator, InMemoryGraphStore, InMemoryVectorStore
        from app.services.processing import ProcessingPipeline
        from app.services.query import DeterministicQueryService
        from app.services.reporting import ReportService
        from app.services.storage import LocalObjectStorage

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
        self.knowledge_graph = KnowledgeGraphAdapter()
        self.rag = CaseScopedRetriever(self.vector)

        # Optional integration hooks: if a real Neo4j URI is configured, provide a config-aware adapter.
        from app.core.config import settings

        if settings.neo4j_uri:
            self.knowledge_graph = KnowledgeGraphAdapter(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)

        if not self.workflow:
            self.workflow = LangGraphInvestigationOrchestrator()


_container: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container
