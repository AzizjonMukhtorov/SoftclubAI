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
        
        prompt = f"""Ты - AI-аналитик образовательной CRM системы Softclub. 
Твоя задача - объяснить администратору, почему студент находится в зоне риска отчисления.

Данные студента:
- Посещаемость: {student_data['attendance_rate']:.1f}%
- Выполнение ДЗ: {student_data['homework_completion']:.1f}%

- Средний балл тестов: {student_data['test_avg_score']:.1f}
- Пропущено занятий подряд: {student_data['missed_classes_streak']} занятий
- Активность общения: {student_data['communication_activity']} взаимодействий
- Дней в системе: {student_data['days_enrolled']} дней

Уровень риска: {risk_level}

Главные факторы риска (по важности):
{factors_text}

Напиши краткое объяснение (максимум 3 предложения) на русском языке, почему этот студент имеет такой уровень риска.
Используй конкретные цифры из данных. Пиши простым языком для администратора."""

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
        prompt = f"""Ты - AI-советник по удержанию студентов в IT-академии Softclub.
Предложи ОДНО наиболее эффективное действие для удержания студента.

Информация о студенте:
- Уровень риска: {risk_level}
- Посещаемость: {student_data['attendance_rate']:.1f}%
- Выполнение ДЗ: {student_data['homework_completion']:.1f}%

- Пропущено подряд: {student_data['missed_classes_streak']} занятий
- Активность общения: {student_data['communication_activity']} взаимодействий

Доступные действия:
1. "Звонок от ментора" - личный звонок от преподавателя
2. "WhatsApp напоминание" - автоматическое напоминание
3. "Встреча с ментором" - назначить личную встречу
4. "Дополнительная поддержка" - предложить помощь с материалами
5. "Гибкий план оплаты" - пересмотреть условия оплаты

Верни ТОЛЬКО валидный JSON в формате:
{{
  "action": "точное название действия из списка выше",
  "reason": "краткое обоснование (1-2 предложения) на русском",
  "success_probability": 0.65,
  "urgency": "high"
}}

Urgency должен быть: "high", "medium" или "low"."""

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
                "action": result.get("action", "Звонок от ментора"),
                "reason": result.get("reason", "Требуется личный контакт"),
                "success_probability": min(max(result.get("success_probability", 0.5), 0), 1),
                "urgency": result.get("urgency", "medium")
            }
        except Exception as e:
            # Fallback рекомендация
            return {
                "action": "Звонок от ментора",
                "reason": f"Рекомендация по умолчанию (ошибка LLM: {str(e)})",
                "success_probability": 0.60,
                "urgency": "high" if risk_level == "High" else "medium"
            }
    
    def _translate_feature(self, feature_name: str) -> str:
        """Переводит название фичи на русский"""
        translations = {
            'attendance_rate': 'Посещаемость',
            'homework_completion': 'Выполнение ДЗ',

            'test_avg_score': 'Средний балл',
            'communication_activity': 'Активность общения',
            'days_enrolled': 'Длительность обучения',
            'missed_classes_streak': 'Пропуски подряд'
        }
        return translations.get(feature_name, feature_name)
