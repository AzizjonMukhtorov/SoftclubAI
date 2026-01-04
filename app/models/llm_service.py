"""
LLM сервис для генерации объяснений и рекомендаций
"""
from groq import Groq
from typing import Dict, Optional
import json
from app.core.config import get_settings


class LLMExplainer:
    """Сервис для генерации AI-объяснений и рекомендаций"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация LLM клиента (Groq)
        
        Args:
            api_key: Groq API ключ (если None, берется из настроек)
        """
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        
        if not self.api_key or self.api_key == "":
            raise ValueError(
                "Groq API key не установлен. "
                "Создайте .env файл и добавьте GROQ_API_KEY=your-key"
            )
        
        self.client = Groq(api_key=self.api_key)
    
    def generate_explanation(
        self, 
        student_data: Dict, 
        risk_level: str,
        feature_importance: Dict[str, float]
    ) -> str:
        """
        Генерирует объяснение причин риска на русском языке
        
        Args:
            student_data: Данные студента (фичи)
            risk_level: Уровень риска (Low/Medium/High)
            feature_importance: Важность каждой фичи
            
        Returns:
            Текстовое объяснение на русском
        """
        # Формируем топ-3 самых важных факторов
        top_factors = sorted(
            feature_importance.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        factors_text = "\n".join([
            f"- {self._translate_feature(name)}: важность {importance:.0%}"
            for name, importance in top_factors
        ])
        
        prompt = f"""You are an AI Analyst for the Softclub Educational CRM system. 
Your task is to explain to an administrator why a student is at risk of dropping out.

Student Data:
- Attendance: {student_data['attendance_rate']:.1f}%
- Homework Completion: {student_data['homework_completion']:.1f}%

- Average Test Score: {student_data['test_avg_score']:.1f}
- Consecutive Missed Classes: {student_data['missed_classes_streak']} classes
- Communication Activity: {student_data['communication_activity']} interactions
- Days Enrolled: {student_data['days_enrolled']} days

Risk Level: {risk_level}

Key Risk Factors (by importance):
{factors_text}

Write a brief explanation (max 3 sentences) in English explaining why this student has this risk level.
Use specific numbers from the data. Write in simple language for an administrator."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Ошибка генерации объяснения: {str(e)}"
    
    def generate_recommendations(
        self, 
        student_data: Dict,
        risk_level: str
    ) -> Dict:
        """
        Генерирует рекомендацию по удержанию студента
        
        Args:
            student_data: Данные студента
            risk_level: Уровень риска
            
        Returns:
            Словарь с рекомендацией:
            {
                "action": "название действия",
                "reason": "обоснование",
                "success_probability": 0.65,
                "urgency": "high/medium/low"
            }
        """
        prompt = f"""You are an AI Retention Advisor for Softclub IT Academy.
Suggest ONE most effective action to retain the student.

Student Information:
- Risk Level: {risk_level}
- Attendance: {student_data['attendance_rate']:.1f}%
- Homework Completion: {student_data['homework_completion']:.1f}%

- Consecutive Missed Classes: {student_data['missed_classes_streak']} classes
- Communication Activity: {student_data['communication_activity']} interactions

Available Actions:
1. "Mentor Call" - personal call from the instructor
2. "WhatsApp Reminder" - automated reminder
3. "Mentor Meeting" - schedule a personal meeting
4. "Additional Support" - offer help with materials
5. "Flexible Payment Plan" - revise payment terms
6. "Do Nothing" - student is doing excellent, no intervention needed

IMPORTANT: If Risk Level is "Low" and metrics are high (Good/Excellent), choose "Do Nothing" or praise. Do not suggest calls or meetings for students who are doing well.

Return ONLY valid JSON in format:
{{
  "action": "exact action name from the list above",
  "reason": "brief justification (1-2 sentences) in English",
  "success_probability": 0.65,
  "urgency": "high/medium/low"
}}

Urgency must be: "high", "medium" or "low"."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Валидация и дефолтные значения
            return {
                "action": result.get("action", "Mentor Call"),
                "reason": result.get("reason", "Personal contact required"),
                "success_probability": min(max(result.get("success_probability", 0.5), 0), 1),
                "urgency": result.get("urgency", "medium")
            }
        except Exception as e:
            # Fallback рекомендация
            return {
                "action": "Mentor Call",
                "reason": f"Default recommendation (LLM error: {str(e)})",
                "success_probability": 0.60,
                "urgency": "high" if risk_level == "High" else "medium"
            }
    
    def _translate_feature(self, feature_name: str) -> str:
        """Переводит название фичи на русский"""
        translations = {
            'attendance_rate': 'Attendance Rate',
            'homework_completion': 'Homework Completion',

            'test_avg_score': 'Average Test Score',
            'communication_activity': 'Communication Activity',
            'days_enrolled': 'Days Enrolled',
            'missed_classes_streak': 'Consecutive Missed Classes'
        }
        return translations.get(feature_name, feature_name)
