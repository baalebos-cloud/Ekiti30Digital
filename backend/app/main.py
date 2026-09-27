from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    admin,
    ask_ekiti,
    contributor_admin,
    contributor_auth,
    health,
    lgas,
    stories,
    timeline,
    uploads,
    vision2056,
)
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(timeline.router)
app.include_router(lgas.router)
app.include_router(stories.router)
app.include_router(vision2056.router)
app.include_router(ask_ekiti.router)
app.include_router(uploads.router)
app.include_router(admin.router)
app.include_router(contributor_auth.router)
app.include_router(contributor_admin.router)
