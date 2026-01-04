"""
Обучение ML модели на сбалансированных данных Softclub + синтетика
Использует 6 features 
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
import xgboost as xgb
import os

def train_model():
    print("=" * 80)
    print("🚀 ОБУЧЕНИЕ ML МОДЕЛИ НА РЕАЛЬНЫХ + СИНТЕТИЧЕСКИХ ДАННЫХ")
    print("=" * 80)
    
    # Загружаем сбалансированный датасет
    print("\n📊 Загрузка данных...")
    df = pd.read_csv('data/training_data_balanced.csv')
    print(f"   ✅ Загружено {len(df)} студентов")
    
    # Проверяем распределение
    print(f"\n📈 Распределение классов:")
    print(f"   churned=0 (активные): {(df['churned'] == 0).sum()} ({(df['churned'] == 0).sum()/len(df)*100:.1f}%)")
    print(f"   churned=1 (отчисленные): {(df['churned'] == 1).sum()} ({(df['churned'] == 1).sum()/len(df)*100:.1f}%)")
    
    # Подготовка данных
    print("\n🔧 Подготовка данных...")
    
    # 6 features (БЕЗ payment_delays и days_since_last_payment)
    feature_names = [
        'attendance_rate',
        'homework_completion',
        'test_avg_score',
        'communication_activity',
        'days_enrolled',
        'missed_classes_streak'
    ]
    
    X = df[feature_names].values
    y = df['churned'].values
    
    print(f"   Features: {len(feature_names)}")
    print(f"   Samples: {len(X)}")
    
    # Разделение на train/test (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📚 Разделение данных:")
    print(f"   Train: {len(X_train)} студентов")
    print(f"   Test: {len(X_test)} студентов")
    
    # Обучение XGBoost
    print("\n🎓 Обучение XGBoost модели...")
    
    model = xgb.XGBClassifier(
        max_depth=5,
        learning_rate=0.05,
        n_estimators=200,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    print("   ✅ Модель обучена!")
    
    # Оценка модели
    print("\n📊 Оценка модели на тестовой выборке:")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Метрики
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"   Accuracy: {accuracy:.2%}")
    print(f"   ROC-AUC: {roc_auc:.2%}")
    
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Active', 'Churned']))
    
    print("\n🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Negatives (правильно предсказали Active): {cm[0][0]}")
    print(f"   False Positives (ошибочно предсказали Churned): {cm[0][1]}")
    print(f"   False Negatives (пропустили Churned): {cm[1][0]}")
    print(f"   True Positives (правильно предсказали Churned): {cm[1][1]}")
    
    # Feature importance
    print("\n🎯 Важность признаков:")
    feature_importance = sorted(
        zip(feature_names, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    
    for feature, importance in feature_importance:
        bar = "█" * int(importance * 50)
        print(f"   {feature:25s} {importance:.3f} {bar}")
    
    # Сохранение модели
    print("\n💾 Сохранение модели...")
    os.makedirs('models/trained', exist_ok=True)
    model_path = 'models/trained/churn_model.json'
    model.save_model(model_path)
    print(f"   ✅ Модель сохранена: {model_path}")
    
    print("\n" + "=" * 80)
    print("🎉 ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    print("=" * 80)
    print(f"\n📌 Модель обучена на:")
    print(f"   - {len(df)} студентов (реальные Softclub + синтетика)")
    print(f"   - 6 features (без payment features)")
    print(f"   - Баланс: {(df['churned'] == 0).sum()/len(df)*100:.1f}% active vs {(df['churned'] == 1).sum()/len(df)*100:.1f}% churned")
    print(f"\n📊 Точность: {accuracy:.2%}")
    print(f"🎯 ROC-AUC: {roc_auc:.2%}")


if __name__ == "__main__":
    train_model()
