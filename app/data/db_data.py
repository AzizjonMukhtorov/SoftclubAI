from typing import List
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Student as DBStudent
from app.api.schemas import Student, StudentFeatures


def get_students() -> List[Student]:
    """Получить всех студентов из БД"""
    db = SessionLocal()
    try:
        db_students = db.query(DBStudent).all()
        
        return [
            Student(
                id=db_student.id,
                name=db_student.name,
                email=db_student.email,
                course=db_student.course,
                features=StudentFeatures(
                    attendance_rate=db_student.attendance_rate,
                    homework_completion=db_student.homework_completion,
                    test_avg_score=db_student.test_avg_score,
                    communication_activity=db_student.communication_activity,
                    days_enrolled=db_student.days_enrolled,
                    missed_classes_streak=db_student.missed_classes_streak
                )
            )
            for db_student in db_students
        ]
    finally:
        db.close()


def get_student_by_id(student_id: int) -> Student:
    """
    Get student by ID from database
    
    Args:
        student_id: Student ID
        
    Returns:
        Student with features
        
    Raises:
        ValueError: If student not found
    """
    db = SessionLocal()
    try:
        db_student = db.query(DBStudent).filter(DBStudent.id == student_id).first()
        
        if not db_student:
            raise ValueError(f"Студент с ID {student_id} не найден")
        
        return Student(
            id=db_student.id,
            name=db_student.name,
            email=db_student.email,
            course=db_student.course,
            features=StudentFeatures(
                attendance_rate=db_student.attendance_rate,
                homework_completion=db_student.homework_completion,
                test_avg_score=db_student.test_avg_score,
                communication_activity=db_student.communication_activity,
                days_enrolled=db_student.days_enrolled,
                missed_classes_streak=db_student.missed_classes_streak
            )
        )
    finally:
        db.close()
