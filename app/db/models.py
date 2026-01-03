"""
Database ORM models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    course = Column(String(255), nullable=False)
    
    attendance_rate = Column(Float, nullable=False)
    homework_completion = Column(Float, nullable=False)
    payment_delays = Column(Integer, nullable=False, default=0)
    days_since_last_payment = Column(Integer, nullable=False, default=0)
    test_avg_score = Column(Float, nullable=False)
    communication_activity = Column(Integer, nullable=False, default=0)
    days_enrolled = Column(Integer, nullable=False, default=0)
    missed_classes_streak = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
