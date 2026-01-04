from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import datetime

from app.db.database import get_db
from app.data.db_data import get_students
from app.models.ml_model import ChurnPredictor
from app.core.config import get_settings
from app.api.schemas import (
    DashboardResponse, 
    RiskDistribution, 
    RiskTrendItem, 
    RootCauseItem, 
    ActionEffectivenessItem, 
    DashboardStats
)

router = APIRouter()
settings = get_settings()

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard_data(db: Session = Depends(get_db)):
    """
    Get aggregated dashboard data.
    Combines real-time ML predictions with some mocked historical data for demo purposes.
    """
    try:
        # 1. Fetch all students
        students = get_students(db)
        total_students = len(students)
        
        # 2. Load ML Model
        predictor = ChurnPredictor(model_path=settings.MODEL_PATH)
        
        # 3. Process each student
        risk_counts = {"Low": 0, "Medium": 0, "High": 0}
        high_risk_factors = {}
        total_confidence = 0
        
        for student in students:
            features = {
                "attendance_rate": student.features.attendance_rate,
                "homework_completion": student.features.homework_completion,
                "test_avg_score": student.features.test_avg_score,
                "communication_activity": student.features.communication_activity,
                "days_enrolled": student.features.days_enrolled,
                "missed_classes_streak": student.features.missed_classes_streak,
            }
            
            risk_level, confidence, factors = predictor.predict(features)
            
            # Count risks
            risk_counts[risk_level] += 1
            total_confidence += confidence
            
            # Aggregate factors for HIGH risk students only
            if risk_level == "High":
                for factor, value in factors.items():
                    # value is importance (higher = more important)
                    high_risk_factors[factor] = high_risk_factors.get(factor, 0) + value

        # 4. Process Aggregates
        
        # Root Causes (Top 5 factors for high risk students)
        root_causes = []
        if high_risk_factors:
            # Sort by total importance
            sorted_factors = sorted(high_risk_factors.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Colors for UI
            colors = {
                "attendance_rate": "#EF4444",      # Red
                "homework_completion": "#F59E0B",  # Orange
                "test_avg_score": "#3B82F6",       # Blue
                "missed_classes_streak": "#8B5CF6",# Purple
                "communication_activity": "#10B981",# Green
                "days_enrolled": "#6B7280"         # Gray
            }
            
            # Human readable names
            names = {
                "attendance_rate": "Attendance",
                "homework_completion": "Homework",
                "test_avg_score": "Grades",
                "missed_classes_streak": "Missed Classes",
                "communication_activity": "Communication",
                "days_enrolled": "Tenure"
            }
            
            total_score = sum(v for k, v in sorted_factors)
            
            for k, v in sorted_factors:
                # Normalize to percentage roughly (just for visual relative size)
                # Or just use raw value scaled
                normalized = (v / total_score) * 100 if total_score > 0 else 0
                
                root_causes.append(RootCauseItem(
                    factor=names.get(k, k),
                    value=round(normalized, 1),
                    color=colors.get(k, "#9CA3AF")
                ))
        
        # 5. Prepare Response
        
        # Stats
        avg_conf = total_confidence / total_students if total_students > 0 else 0
        
        stats = DashboardStats(
            totalStudents=total_students,
            atRiskStudents=risk_counts["High"],
            riskChange=-3, # Mocked improvement
            avgConfidence=round(avg_conf, 2),
            actionsThisWeek=12, # Mocked
            successfulActions=8 # Mocked
        )
        
        # Distribution
        distribution = RiskDistribution(
            low=risk_counts["Low"],
            medium=risk_counts["Medium"],
            high=risk_counts["High"],
            total=total_students
        )
        
        # Mocked Trends (Last 8 weeks)
        # We'll generate dates dynamically backwards from today
        trends = []
        today = datetime.date.today()
        for i in range(8):
            week_date = today - datetime.timedelta(weeks=7-i)
            # Create some variance based on current counts to make it look realistic but changing
            # Just simple hardcoded pattern matching the requested structure
            trends.append(RiskTrendItem(
                week=f"Week {i+1}",
                date=week_date.strftime("%Y-%m-%d"),
                low=40 + i, # Improving trend
                medium=30 - (i % 2),
                high=25 - i # Decreasing risk
            ))
            
        # Mocked Actions
        actions = [
            ActionEffectivenessItem(action="Mentor Call", successRate=65, color="#10B981"),
            ActionEffectivenessItem(action="Parent Meeting", successRate=55, color="#3B82F6"),
            ActionEffectivenessItem(action="Personal Chat", successRate=45, color="#8B5CF6"),
            ActionEffectivenessItem(action="WhatsApp", successRate=30, color="#F59E0B"),
            ActionEffectivenessItem(action="No Action", successRate=10, color="#EF4444"),
        ]
        
        return DashboardResponse(
            riskDistribution=distribution,
            riskTrend=trends,
            rootCauses=root_causes,
            actionsEffectiveness=actions,
            stats=stats
        )
        
    except Exception as e:
        print(f"Error generating dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
