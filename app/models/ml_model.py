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
        
        # Предсказание вероятностей для каждого класса
        probs = self.model.predict(dmatrix)[0]  # [prob_low, prob_medium, prob_high]
        
        risk_class = np.argmax(probs)
        confidence = float(np.max(probs))
        
        risk_level = {0: 'Low', 1: 'Medium', 2: 'High'}[risk_class]
        
        # Feature importance
        feature_importance = self._get_feature_importance(features)
        
        return risk_level, confidence, feature_importance
    
    def _prepare_features(self, features: Dict) -> np.ndarray:
        """Подготовить фичи для модели"""
        X = np.array([[features[name] for name in self.feature_names]])
        return X
    
    def _get_feature_importance(self, features: Dict) -> Dict[str, float]:
        """
        Получить важность фич из обученной модели
        """
        # Используем встроенную feature importance из XGBoost
        importance = self.model.get_score(importance_type='weight')
        
        # Преобразуем технические имена (f0, f1) в человекочитаемые
        readable_importance = {}
        for key, value in importance.items():
            # XGBoost использует f0, f1, f2... вместо имен
            if key.startswith('f'):
                try:
                    feature_index = int(key[1:])  # f0 → 0, f1 → 1
                    if feature_index < len(self.feature_names):
                        feature_name = self.feature_names[feature_index]
                        readable_importance[feature_name] = value
                except (ValueError, IndexError):
                    readable_importance[key] = value
            else:
                readable_importance[key] = value
        
        # Нормализуем
        total = sum(readable_importance.values())
        if total > 0:
            return {k: v/total for k, v in readable_importance.items()}
        else:
            return readable_importance
