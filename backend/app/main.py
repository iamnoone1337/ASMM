from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .logging_config import configure_logging
from .api.routes.health import router as health_router
from .api.routes.scan import router as scan_router
from .api.routes.assets import router as assets_router

configure_logging()
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(scan_router, prefix=settings.API_V1_PREFIX)
app.include_router(assets_router, prefix=settings.API_V1_PREFIX)