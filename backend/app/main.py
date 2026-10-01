import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    admin,
    ask_ekiti,
    content_admin,
    contributor_admin,
    contributor_auth,
    health,
    homepage,
    homepage_admin,
    lgas,
    stories,
    timeline,
    uploads,
    vision2056,
)
from app.core.config import settings

# Uvicorn only configures its own loggers, so without this every app.*
# logger.info (e.g. the admin write lines in content_admin.py) is dropped.
_app_logger = logging.getLogger("app")
if not _app_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:     %(name)s: %(message)s"))
    _app_logger.addHandler(_handler)
    _app_logger.setLevel(logging.INFO)

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
app.include_router(content_admin.lgas_router)
app.include_router(content_admin.timeline_router)
app.include_router(homepage.router)
for _router in homepage_admin.routers:
    app.include_router(_router)
