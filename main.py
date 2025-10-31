from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import voice
from app.api import note

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - basic health check."""
    return {
        "message": "Trunq Backend API",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Include API routers
app.include_router(voice.router, prefix=f"{settings.api_v1_prefix}/voice", tags=["voice"])
app.include_router(note.router, prefix=f"{settings.api_v1_prefix}/note", tags=["note"])
