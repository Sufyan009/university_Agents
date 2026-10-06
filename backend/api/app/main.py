"""Main FastAPI application."""
import logging
import uuid
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.auth.routes import router as auth_router
from app.roles.routes import router as roles_router
from app.university.routes import router as university_router
from app.admin.universities.routes import router as admin_universities_router
from app.courses.routes import router as courses_router
from app.subjects.routes import router as subjects_router
from app.admissions.routes import router as admissions_router
from app.scholarships.routes import router as scholarships_router
from app.faqs.routes import router as faqs_router
from app.calls.routes import router as calls_router
from app.config import get_settings
from app.database import close_database_connection, connect_to_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API for University Voice Agent — Auth, Universities, Courses, Subjects, Admissions, Agent Settings",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    await connect_to_database()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await close_database_connection()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start_time = datetime.utcnow()
    logger.info(f"[{request_id}] {request.method} {request.url.path} - Started")
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"[{request_id}] {request.method} {request.url.path} - Completed {response.status_code} in {duration:.3f}s")
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled exception: {exc}", exc_info=True)
    settings = get_settings()
    detail = str(exc) if settings.debug else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"detail": detail, "request_id": request_id, "timestamp": datetime.utcnow().isoformat()},
    )


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.app_name, "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {"message": f"Welcome to {settings.app_name}", "docs": "/docs" if settings.debug else None, "version": "1.0.0"}


# Include routers
app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(university_router)
app.include_router(admin_universities_router)
app.include_router(courses_router)
app.include_router(subjects_router)
app.include_router(admissions_router)
app.include_router(scholarships_router)
app.include_router(faqs_router)
app.include_router(calls_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
