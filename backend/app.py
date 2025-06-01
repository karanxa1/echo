from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import create_tables
from config import settings
from api import auth, memories, chat, replicas
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="ECHO API",
    description="Your Life, Remembered Forever - AI-powered personal memory and legacy system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Include routers
app.include_router(auth.router)
app.include_router(memories.router)
app.include_router(chat.router)
app.include_router(replicas.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to ECHO - Your Life, Remembered Forever",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ECHO API",
        "version": "1.0.0"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()
    print("ECHO API is starting up...")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"CORS origins: {settings.FRONTEND_URL}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("ECHO API is shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    ) 