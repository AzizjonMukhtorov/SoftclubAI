import numpy as np
import xgboost as xgb
from typing import Dict, Tuple, Optional
import os


class ChurnPredictor:
    """Предсказатель риска оттока студента"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Инициализация модели
        
        Args:
            model_path: Путь к сохраненной модели (по умолчанию models/trained/churn_model.json)
        """
        self.model = None
        self.feature_names = [
            'attendance_rate',
            'homework_completion',
            'test_avg_score',
            'communication_activity',
            'days_enrolled',
            'missed_classes_streak'
        ]
        
        # Используем дефолтный путь если не указан
        if model_path is None:
            model_path = 'models/trained/churn_model.json'
        
        # Загружаем модель
        if os.path.exists(model_path):
            self.model = xgb.Booster()
            self.model.load_model(model_path)
            print(f"✅ ML модель загружена: {model_path}")
        else:
            print(f"⚠️  ВНИМАНИЕ: Модель не найдена по пути: {model_path}")
            print(f"   Обучите модель командой: python train_improved_model.py")
            raise FileNotFoundError(f"ML модель не найдена: {model_path}")
    
    def predict(self, features: Dict) -> Tuple[str, float, Dict[str, float]]:
        """
        Предсказать риск оттока студента
        
        Args:
            features: Словарь с фичами студента
            
        Returns:
            (risk_level, confidence, feature_importance)
            - risk_level: 'Low', 'Medium', 'High'
            - confidence: уверенность модели (0-1)
            - feature_importance: важность каждой фичи
        """
        if self.model is None:
            raise ValueError("Модель не загружена! Убедитесь что файл модели существует.")
        
        return self._predict_with_model(features)
    
    def _predict_with_model(self, features: Dict) -> Tuple[str, float, Dict[str, float]]:
        """Предсказание с использованием обученной XGBoost модели"""
        X = self._prepare_features(features)
        dmatrix = xgb.DMatrix(X, feature_names=self.feature_names)
        
        # Получаем вероятность отчисления (binary classification)
        churn_probability = float(self.model.predict(dmatrix)[0])
        
        # Определяем уровень риска по порогам вероятности
        # Пороги обновлены для High Recall (0.40 threshold)
        if churn_probability < 0.40:
            risk_level = 'Low'
            risk_class = 0
        elif churn_probability < 0.70:
            risk_level = 'Medium'
            risk_class = 1
        else:
            risk_level = 'High'
            risk_class = 2
        
        # Confidence - насколько уверены в предсказании
        confidence = abs(churn_probability - 0.5) * 2  # 0-1 scale
        
        # Feature importance
        feature_importance = self._get_feature_importance(features)
        
        return risk_level, float(confidence), feature_importance
    
    def _prepare_features(self, features: Dict) -> np.ndarray:
        """Подготовить фичи для модели"""
        X = np.array([[features[name] for name in self.feature_names]])
        return X
    
    def _get_feature_importance(self, features: Dict) -> Dict[str, float]:
        """
        Получить индивидуальный вклад каждого признака для конкретного студента
        """
        # Получаем глобальную важность признаков из модели
        try:
            global_importance = self.model.get_score(importance_type='weight')
        except:
            # Если модель не имеет get_score, используем feature_importances
            global_importance = {}
            for i, name in enumerate(self.feature_names):
                global_importance[f'f{i}'] = 1.0 / len(self.feature_names)
        
        # Преобразуем технические имена (f0, f1) в человекочитаемые
        readable_importance = {}
        for key, value in global_importance.items():
            if key.startswith('f'):
                try:
                    feature_index = int(key[1:])
                    if feature_index < len(self.feature_names):
                        feature_name = self.feature_names[feature_index]
                        readable_importance[feature_name] = value
                except (ValueError, IndexError):
                    readable_importance[key] = value
            else:
                readable_importance[key] = value
        
        # Взвешиваем важность на основе ЗНАЧЕНИЙ признаков студента
        # Чем ниже значение (хуже показатель), тем больше вклад в риск
        weighted_importance = {}
        for feature_name in self.feature_names:
            global_weight = readable_importance.get(feature_name, 1.0)
            feature_value = features.get(feature_name, 50.0)
            
            # Для признаков, где меньше = хуже (attendance, homework, test_score)
            if feature_name in ['attendance_rate', 'homework_completion', 'test_avg_score']:
                # Инвертируем: низкое значение = высокая важность
                risk_factor = (100 - feature_value) / 100.0
            # Для missed_classes_streak: больше = хуже
            elif feature_name == 'missed_classes_streak':
                risk_factor = min(feature_value / 15.0, 1.0)  # Нормализуем к 0-1
            # Для остальных используем как есть
            else:
                risk_factor = 0.5
            
            weighted_importance[feature_name] = global_weight * (0.5 + risk_factor)
        
        # Нормализуем к сумме = 1
        total = sum(weighted_importance.values())
        if total > 0:
            return {k: v/total for k, v in weighted_importance.items()}
        else:
            return weighted_importance
