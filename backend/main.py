import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session

from config import settings
from database.session import engine, Base, get_db
from routes import auth, papers, analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS Middleware
origins = [settings.FRONTEND_URL] + settings.BACKEND_CORS_ORIGINS
if "*" in settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "error": exc.detail,
                "detail": str(exc) if not settings.VERSION.startswith("3") else None
            }
        )
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "data": None,
                "error": "Validation Error",
                "detail": exc.errors()
            }
        )
    
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": "Internal Server Error",
            "detail": str(exc) if not settings.VERSION.startswith("3") else None
        }
    )


# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(papers.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)


@app.get("/")
def home():
    return {
        "success": True,
        "data": {"message": "ResearchGap AI Backend Running", "version": settings.VERSION},
        "error": None
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_ok = False
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error(f"Health check: Database connection failed: {e}")

    return {
        "success": True,
        "data": {
            "status": "ok" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "version": settings.VERSION, 
            "intelligence_layer": "active"
        },
        "error": None if db_ok else "Database connection failed"
    }
