from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.container import get_container
from app.core.config import settings
from app.core.security import hash_password
from app.models.domain import Role, User
from app.routers import auth, cases, evidence, graph, health, investigation

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def seed_demo_users() -> None:
    container = get_container()
    seed_users = [
        ("admin", settings.demo_admin_password, Role.admin),
        ("investigator", settings.demo_investigator_password, Role.investigator),
        ("analyst", settings.demo_analyst_password, Role.analyst),
    ]
    for username, password, role in seed_users:
        if not container.repository.get_user_by_username(username):
            container.repository.upsert_user(
                User(username=username, password_hash=hash_password(password), role=role)
            )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.cors_origins.split(",") if item.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": f"Internal server error: {exc.__class__.__name__}"})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(investigation.router)
app.include_router(graph.router)
