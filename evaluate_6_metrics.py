"""
Комплексная оценка ML модели на реальных данных Softclub (data/softclub_training.csv)
Показывает 6 ключевых метрик: Accuracy, Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix
"""
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from sklearn.model_selection import train_test_split
import xgboost as xgb
import os

def evaluate_model():
    print("=" * 80)
    print("📊 ЭКСПРЕСС-ТЕСТ МОДЕЛИ: 6 МЕТРИК")
    print("=" * 80)
    
    # 1. Загрузка модели
    model_path = 'models/trained/churn_model.json'
    if not os.path.exists(model_path):
        print(f"❌ Ошибка: Модель не найдена по пути {model_path}")
        return

    print("\n📦 Загрузка обученной модели...")
    model = xgb.Booster()
    model.load_model(model_path)
    print("   ✅ Модель успешно загружена")
    
    # 2. Загрузка реальных данных
    data_path = 'data/softclub_training.csv'
    print(f"\n📊 Загрузка данных из {data_path}...")
    df = pd.read_csv(data_path)
    
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
    
    # 3. Выделение тестовой выборки (как при обучении)
    # Важно: используем тот же random_state=42, чтобы получить ТУ ЖЕ тестовую выборку
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   ✅ Тестовая выборка: {len(X_test)} студентов")
    print(f"      - Active: {(y_test == 0).sum()}")
    print(f"      - Churned: {(y_test == 1).sum()}")
    
    # 4. Предсказания
    print("\n🔮 Генерация предсказаний...")
    dtest = xgb.DMatrix(X_test, feature_names=feature_names)
    y_pred_proba = model.predict(dtest)
    y_pred = (y_pred_proba >= 0.40).astype(int)
    
    # ============================================================
    # 5. РАСЧЕТ И ВЫВОД МЕТРИК
    # ============================================================
    
    # 1. Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    
    # 2. Precision
    precision = precision_score(y_test, y_pred)
    
    # 3. Recall
    recall = recall_score(y_test, y_pred)
    
    # 4. F1-Score
    f1 = f1_score(y_test, y_pred)
    
    # 5. ROC-AUC
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    # 6. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    print("\n" + "-" * 40)
    print("📈 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("-" * 40)
    print(f"1️⃣  Accuracy:   {accuracy:.2%}  (Точность)")
    print(f"2️⃣  Precision:  {precision:.2%}  (Точность 'отчисленных')")
    print(f"3️⃣  Recall:     {recall:.2%}  (Полнота - сколько нашли)")
    print(f"4️⃣  F1-Score:   {f1:.2%}  (Баланс)")
    print(f"5️⃣  ROC-AUC:    {roc_auc:.2%}  (Качество вероятностей)")
    
    print("\n6️⃣  Confusion Matrix (Матрица Ошибок):")
    print(f"    [[TN={tn:<3}  FP={fp:<3}]")
    print(f"     [FN={fn:<3}  TP={tp:<3}]]")
    
    print("\n💡 Расшифровка:")
    print(f"   ✅ Правильно предсказали 'Учится': {tn}")
    print(f"   ✅ Правильно предсказали 'Отчислен': {tp}")
    print(f"   ❌ ОШИБКА: Сказали 'отчислится', а он учится: {fp}")
    print(f"   ❌ ОШИБКА: Студент ОТЧИСЛИЛСЯ, а мы пропустили: {fn} (Самая опасная ошибка!)")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    evaluate_model()
