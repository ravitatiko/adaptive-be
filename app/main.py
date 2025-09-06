from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.mongodb import connect_to_mongo, close_mongo_connection
from app.api.api_v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Adaptive Learning Platform",
        "version": settings.version,
        "docs": "/docs",
        "api": settings.api_v1_prefix
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    from app.core.mongodb import test_mongodb_connection
    mongodb_status = test_mongodb_connection()
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "mongodb": "connected" if mongodb_status else "disconnected"
    }


# Test endpoint for course API (no authentication)
@app.get("/course/{course_id}/assets")
async def test_course_assets(course_id: str):
    """Test endpoint for course assets (no authentication)"""
    try:
        from app.core.mongodb import get_database
        from app.services.course_service import CourseService
        
        db = get_database()
        if db is None:
            return {"error": "Database not connected"}
        
        course_service = CourseService(db)
        course = await course_service.get_course_with_assets(course_id)
        
        if course:
            return course
        else:
            return {"error": "Course not found"}
            
    except Exception as e:
        return {"error": str(e)}


# Test endpoint for course API with user progress (no authentication)
@app.get("/course/{course_id}/assets/progress/{user_id}")
async def test_course_assets_with_progress(course_id: str, user_id: str):
    """Test endpoint for course assets with user progress (no authentication)"""
    try:
        from app.core.mongodb import get_database
        from app.services.course_service import CourseService
        
        db = get_database()
        if db is None:
            return {"error": "Database not connected"}
        
        course_service = CourseService(db)
        course = await course_service.get_course_with_user_progress(course_id, user_id)
        
        if course:
            return course
        else:
            return {"error": "Course not found"}
            
    except Exception as e:
        return {"error": str(e)}


# Test endpoint for translation API (no authentication)
@app.post("/test-translate")
async def test_translate_asset(
    asset_code: str = Form(...),
    target_language: str = Form(...),
    content: str = Form(...)
):
    """Test endpoint for translation API (no authentication)"""
    try:
        from app.core.mongodb import get_database
        from app.services.translation_service import TranslationService
        
        db = get_database()
        if db is None:
            return {"error": "Database not connected"}
        
        # Validate target language
        if target_language not in ["hi", "te"]:
            return {"error": "Target language must be 'hi' (Hindi) or 'te' (Telugu)"}
        
        translation_service = TranslationService(db)
        translation = await translation_service.create_translation(
            asset_code=asset_code,
            target_language=target_language,
            content=content
        )
        
        if translation:
            return translation
        else:
            return {"error": "Translation failed"}
            
    except Exception as e:
        return {"error": str(e)}


# Test endpoint for getting translations (no authentication)
@app.get("/test-translations/{asset_code}")
async def test_get_translations(asset_code: str):
    """Test endpoint for getting available translations (no authentication)"""
    try:
        from app.core.mongodb import get_database
        from app.services.translation_service import TranslationService
        
        db = get_database()
        if db is None:
            return {"error": "Database not connected"}
        
        translation_service = TranslationService(db)
        translations = await translation_service.get_available_translations(asset_code)
        
        return translations
            
    except Exception as e:
        return {"error": str(e)}


# Test endpoint for asset summary generation (no authentication)
@app.post("/test-asset-summary")
async def test_asset_summary(asset_id: str = Form(...)):
    """Test endpoint for asset summary generation (no authentication)"""
    try:
        from app.core.mongodb import get_database
        from app.services.asset_summary_service import AssetSummaryService
        
        db = get_database()
        if db is None:
            return {"error": "Database not connected"}
        
        asset_summary_service = AssetSummaryService(db)
        updated_asset = await asset_summary_service.generate_and_update_summary(asset_id)
        
        if updated_asset:
            return updated_asset
        else:
            return {"error": "Asset summary generation failed"}
            
    except Exception as e:
        return {"error": str(e)}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
