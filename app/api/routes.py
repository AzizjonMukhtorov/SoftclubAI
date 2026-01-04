"""
FastAPI роуты для API прогнозирования оттока студентов
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.api.schemas import (
    StudentRiskListResponse,
    StudentListResponse,
    RiskAssessment,
    DetailedAnalysis,
    Recommendation
)
from app.data.db_data import get_students, get_student_by_id  # ← Database instead of mock
from app.models.ml_model import ChurnPredictor
from app.models.llm_service import LLMExplainer
from app.core.config import get_settings

# Инициализация роутера
router = APIRouter(prefix="/api", tags=["Student Churn Prediction"])

# Инициализация моделей (singleton pattern)
settings = get_settings()
ml_model = ChurnPredictor(model_path=settings.MODEL_PATH)
llm_explainer = None  # Будет инициализирован при первом использовании


def get_llm_explainer() -> LLMExplainer:
    """Ленивая инициализация LLM клиента"""
    global llm_explainer
    if llm_explainer is None:
        try:
            llm_explainer = LLMExplainer()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM сервис не настроен: {str(e)}"
            )
    return llm_explainer


@router.get("/students/risks", response_model=StudentRiskListResponse)
async def get_student_risks():
    """
    Получить список всех студентов с оценкой риска
    
    Returns:
        Список студентов с риск-уровнями (Low/Medium/High)
    """
    students = get_students()
    risk_assessments: List[RiskAssessment] = []
    
    for student in students:
        # Преобразуем Pydantic модель в dict для ML модели
        features_dict = student.features.model_dump()
        
        # Получаем предсказание
        risk_level, confidence, _ = ml_model.predict(features_dict)
        
        risk_assessments.append(
            RiskAssessment(
                student_id=student.id,
                student_name=student.name,
                student_course_name=student.course,
                student_phone_number=student.student_phone_number,
                risk_level=risk_level,
                confidence=round(confidence, 2)
            )
        )
    
    return StudentRiskListResponse(
        total=len(risk_assessments),
        students=risk_assessments
    )


@router.get("/students/{student_id}/analysis", response_model=DetailedAnalysis)
async def get_student_analysis(student_id: int):
    """
    Получить детальный анализ студента с AI-объяснениями и рекомендациями
    
    Args:
        student_id: ID студента
        
    Returns:
        Полный анализ: риск, объяснение, рекомендации, ключевые факторы
    """
    # Получаем данные студента
    try:
        student = get_student_by_id(student_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Студент с ID {student_id} не найден")
    
    features_dict = student.features.model_dump()
    
    # ML предсказание
    risk_level, confidence, feature_importance = ml_model.predict(features_dict)
    
    # LLM объяснение и рекомендации
    llm = get_llm_explainer()
    
    try:
        explanation = llm.generate_explanation(
            features_dict,
            risk_level,
            feature_importance
        )
        
        recommendation_data = llm.generate_recommendations(
            features_dict,
            risk_level
        )
        
        recommendation = Recommendation(**recommendation_data)
        
    except Exception as e:
        # Fallback если LLM не работает
        explanation = f"Студент в зоне риска '{risk_level}'. (LLM недоступен: {str(e)})"
        recommendation = Recommendation(
            action="Связаться со студентом",
            reason="Рекомендация по умолчанию",
            success_probability=0.5,
            urgency="medium"
        )
    
    return DetailedAnalysis(
        student=student,
        risk_level=risk_level,
        confidence=round(confidence, 2),
        explanation=explanation,
        recommendation=recommendation,
        key_factors=feature_importance
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Student Churn Prediction API",
        "ml_model": "loaded" if ml_model.model is not None else "not loaded"
    }


@router.get("/students", response_model=StudentListResponse)
async def get_students_list():
    """
    Получить список всех студентов с их данными (без ML предсказаний)
    
    Returns:
        Список всех студентов с features
    """
    students = get_students()
    
    return StudentListResponse(
        total=len(students),
        students=students
    )
