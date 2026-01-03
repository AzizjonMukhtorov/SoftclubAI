from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI модуль прогнозирования оттока студентов для Softclub CRM",
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    """Корневой endpoint - информация об API"""
    return {
        "message": "Student Churn Prediction API",
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "list_risks": "/api/students/risks",
            "detailed_analysis": "/api/students/{student_id}/analysis",
            "health": "/api/health"
        }
    }




def main():
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
