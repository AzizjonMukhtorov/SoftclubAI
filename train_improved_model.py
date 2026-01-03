import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data.realistic_data_generator import generate_realistic_training_data


def train_improved_model(n_samples: int = 15000):
    """
    Обучает УЛУЧШЕННУЮ XGBoost модель на реалистичных данных
    Цель: точность 70-80%
    
    Args:
        n_samples: Количество тренировочных примеров (рекомендуется 15000+)
    """
    print("=" * 80)
    print("🚀 Обучение УЛУЧШЕННОЙ XGBoost модели (цель: 70-80% accuracy)")
    print(f"   📊 Датасет: {n_samples} РЕАЛИСТИЧНЫХ примеров")
    print("=" * 80)
    
    # Шаг 1: Генерация РЕАЛИСТИЧНЫХ данных
    df = generate_realistic_training_data(
        n_samples=n_samples,
        low_ratio=0.45,     # 45% низкий риск
        medium_ratio=0.30,  # 30% средний риск
        high_ratio=0.25     # 25% высокий риск
    )
    
    # Показываем распределение классов
    print("\\n📈 Распределение классов:")
    class_counts = df['risk_label'].value_counts().sort_index()
    for label, count in class_counts.items():
        risk_name = {0: 'Low', 1: 'Medium', 2: 'High'}[label]
        print(f"   {risk_name} Risk: {count} ({count/len(df)*100:.1f}%)")
    
    # Шаг 2: Подготовка данных
    print("\\n🔧 Подготовка данных для обучения...")
    
    feature_columns = [
        'attendance_rate',
        'homework_completion',
        'payment_delays',
        'days_since_last_payment',
        'test_avg_score',
        'communication_activity',
        'days_enrolled',
        'missed_classes_streak'
    ]
    
    X = df[feature_columns].values
    y = df['risk_label'].values
    
    # Разделяем на train/test (85/15 для большего обучающего сета)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    
    print(f"   Обучающая выборка: {len(X_train)} примеров")
    print(f"   Тестовая выборка: {len(X_test)} примеров")
    
    # Шаг 3: Обучение ОПТИМИЗИРОВАННОЙ XGBoost модели
    print("\\n🤖 Обучение оптимизированной XGBoost модели...")
    
    model = xgb.XGBClassifier(
        n_estimators=300,          # Больше деревьев для лучшей точности
        max_depth=7,               # Глубже для сложных паттернов
        learning_rate=0.03,        # Медленное обучение = лучшая точность
        min_child_weight=1,        # Меньше ограничений
        subsample=0.85,            # 85% данных на итерацию
        colsample_bytree=0.85,     # 85% признаков на дерево
        gamma=0.05,                # Меньше gamma = больше splits
        reg_alpha=0.1,             # L1 регуляризация
        reg_lambda=1.0,            # L2 регуляризация
        objective='multi:softprob',
        num_class=3,
        random_state=42,
        verbosity=0,
        early_stopping_rounds=20   # Остановка если не улучшается
    )
    
    # Обучение с validation set для early stopping
    eval_set = [(X_test, y_test)]
    model.fit(
        X_train, y_train,
        eval_set=eval_set,
        verbose=False
    )
    print("   ✅ Модель обучена с early stopping!")
    
    # Шаг 4: Оценка качества
    print("\\n📊 Оценка качества модели:")
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\\n   🎯 Точность (Accuracy): {accuracy:.2%}")
    
    print("\\n   📋 Classification Report:")
    target_names = ['Low Risk', 'Medium Risk', 'High Risk']
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    print("   🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("      Predicted:  Low  Med  High")
    for i, row in enumerate(cm):
        actual = target_names[i]
        print(f"   {actual:12s}  {row[0]:3d}  {row[1]:3d}  {row[2]:3d}")
    
    # Шаг 5: Feature Importance
    print("\\n📈 Feature Importance (важность фич):")
    importance_dict = dict(zip(feature_columns, model.feature_importances_))
    sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
    
    for feature, importance in sorted_importance:
        bar = "█" * int(importance * 60)
        print(f"   {feature:25s} {importance:.3f} {bar}")
    
    # Шаг 6: Сохранение модели
    print("\\n💾 Сохранение улучшенной модели...")
    
    os.makedirs('models/trained', exist_ok=True)
    
    model_path = 'models/trained/churn_model.json'
    model.save_model(model_path)
    
    print(f"   ✅ Модель сохранена в: {model_path}")
    print(f"   📦 Размер файла: {os.path.getsize(model_path) / 1024:.1f} KB")
    
    # Шаг 7: Тест предсказания
    print("\\n🧪 Тестовое предсказание:")
    
    test_cases = [
        {
            'name': 'Отличный студент',
            'data': {
                'attendance_rate': 95.0,
                'homework_completion': 92.0,
                'payment_delays': 0,
                'days_since_last_payment': 5,
                'test_avg_score': 90.0,
                'communication_activity': 18,
                'days_enrolled': 90,
                'missed_classes_streak': 0
            }
        },
        {
            'name': 'Проблемный студент',
            'data': {
                'attendance_rate': 35.0,
                'homework_completion': 40.0,
                'payment_delays': 5,
                'days_since_last_payment': 60,
                'test_avg_score': 45.0,
                'communication_activity': 2,
                'days_enrolled': 60,
                'missed_classes_streak': 6
            }
        }
    ]
    
    for case in test_cases:
        X_new = np.array([[case['data'][col] for col in feature_columns]])
        prediction = model.predict(X_new)[0]
        probabilities = model.predict_proba(X_new)[0]
        
        risk_level = {0: 'Low', 1: 'Medium', 2: 'High'}[prediction]
        
        print(f"\\n   {case['name']}:")
        print(f"   ➡️  Прогноз: {risk_level} Risk (Low: {probabilities[0]:.0%}, Med: {probabilities[1]:.0%}, High: {probabilities[2]:.0%})")
    
    print("\\n" + "=" * 80)
    if accuracy >= 0.70:
        print("✅ Цель достигнута! Точность ≥ 70%")
    else:
        print(f"⚠️  Точность {accuracy:.1%} - нужно еще улучшение")
    print("=" * 80)
    print("\\n💡 Модель готова к использованию!")
    print("\\n")


if __name__ == "__main__":
    # Обучаем на 15000 реалистичных примерах
    train_improved_model(n_samples=15000)
