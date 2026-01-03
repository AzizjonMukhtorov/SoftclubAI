from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class StudentFeatures(BaseModel):
    attendance_rate: float = Field(..., ge=0, le=100, description="% посещаемости")
    homework_completion: float = Field(..., ge=0, le=100, description="% выполненных ДЗ")
    payment_delays: int = Field(..., ge=0, description="Количество задержек оплаты")
    days_since_last_payment: int = Field(..., ge=0, description="Дней с последней оплаты")
    test_avg_score: float = Field(..., ge=0, le=100, description="Средний балл тестов")
    communication_activity: int = Field(..., ge=0, description="Активность общения")
    days_enrolled: int = Field(..., ge=0, description="Дней в системе")
    missed_classes_streak: int = Field(..., ge=0, description="Пропусков подряд")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attendance_rate": 75.5,
                "homework_completion": 80.0,
                "payment_delays": 1,
                "days_since_last_payment": 15,
                "test_avg_score": 72.3,
                "communication_activity": 12,
                "days_enrolled": 90,
                "missed_classes_streak": 2
            }
        }


class Student(BaseModel):
    """Модель студента"""
    id: int
    name: str
    email: str
    course: str
    features: StudentFeatures


class RiskAssessment(BaseModel):
    """Оценка риска студента"""
    student_id: int
    student_name: str
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1, description="Уверенность модели")


class StudentListResponse(BaseModel):
    """Список студентов с полными данными (без ML предсказаний)"""
    total: int = Field(..., description="Общее количество студентов")
    students: List[Student] = Field(..., description="Список студентов")


class Recommendation(BaseModel):
    """Рекомендация по удержанию студента"""
    action: str = Field(..., description="Рекомендуемое действие")
    reason: str = Field(..., description="Обоснование рекомендации")
    success_probability: float = Field(..., ge=0, le=1, description="Вероятность успеха")
    urgency: str = Field(..., description="Уровень срочности: high/medium/low")


class DetailedAnalysis(BaseModel):
    """Детальный анализ студента"""
    student: Student
    risk_level: RiskLevel
    confidence: float
    explanation: str = Field(..., description="AI объяснение причин риска")
    recommendation: Recommendation
    key_factors: Dict[str, float] = Field(..., description="Ключевые факторы влияния")


class StudentRiskListResponse(BaseModel):
    """Ответ со списком студентов и их рисками"""
    total: int
    students: List[RiskAssessment]
