"""
Обучение модели ТОЛЬКО на реальных данных Softclub
Без синтетики - 645 churned + 1028 successful = 1673 студентов
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import os

def train_on_real_data():
    print("=" * 80)
    print("🚀 ОБУЧЕНИЕ ТОЛЬКО НА РЕАЛЬНЫХ ДАННЫХ SOFTCLUB")
    print("=" * 80)
    
    # Загружаем ТОЛЬКО реальные данные
    print("\n📊 Загрузка данных...")
    df = pd.read_csv('data/softclub_training.csv')
    print(f"   ✅ Загружено {len(df)} РЕАЛЬНЫХ студентов Softclub")
    print(f"      - churned=0 (успешные): {(df['churned'] == 0).sum()}")
    print(f"      - churned=1 (отчислены): {(df['churned'] == 1).sum()}")
    
    # Подготовка данных
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
    
    # Train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📚 Разделение данных:")
    print(f"   Train: {len(X_train)} студентов")
    print(f"      - churned=0: {(y_train == 0).sum()}")
    print(f"      - churned=1: {(y_train == 1).sum()}")
    print(f"   Test: {len(X_test)} студентов")
    print(f"      - churned=0: {(y_test == 0).sum()}")
    print(f"      - churned=1: {(y_test == 1).sum()}")
    
    # Обучение XGBoost
    print("\n🎓 Обучение XGBoost модели на реальных данных...")
    
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
    model.get_booster().save_model(model_path)  # Исправлено!
    print(f"   ✅ Модель сохранена: {model_path}")
    
    # Оценка модели
    print("\n" + "=" * 80)
    print("📊 ОЦЕНКА НА ТЕСТОВОЙ ВЫБОРКЕ")
    print("=" * 80)
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Метрики
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\n📈 Метрики:")
    print(f"   Accuracy:  {accuracy:.2%}")
    print(f"   Precision: {precision:.2%}")
    print(f"   Recall:    {recall:.2%}")
    print(f"   F1-Score:  {f1:.2%}")
    print(f"   ROC-AUC:   {roc_auc:.2%}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    print(f"\n📋 Confusion Matrix:")
    print(cm)
    print(f"\n   TN (правильно active):  {tn}")
    print(f"   FP (ошибочно churned):  {fp}")
    print(f"   FN (пропустили churned): {fn}")
    print(f"   TP (правильно churned): {tp}")
    
    # Детальный отчет
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Active/Graduated', 'Churned']))
    
    # Cross-validation
    print("\n" + "=" * 80)
    print("🔄 5-FOLD CROSS-VALIDATION")
    print("=" * 80)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    print(f"\n📊 Метрики по всем фолдам:")
    for metric_name, metric in [('Accuracy', 'accuracy'), ('Recall', 'recall'), ('Precision', 'precision'), ('F1', 'f1'), ('ROC-AUC', 'roc_auc')]:
        scores = cross_val_score(model, X, y, cv=cv, scoring=metric)
        print(f"   {metric_name:10s}: {scores.mean():.2%} ± {scores.std():.2%}")
    
    # Распределение вероятностей
    print("\n" + "=" * 80)
    print("📈 РАСПРЕДЕЛЕНИЕ ВЕРОЯТНОСТЕЙ НА ВСЕХ ДАННЫХ")
    print("=" * 80)
    
    y_all_pred_proba = model.predict_proba(X)[:, 1]
    
    print(f"\n   Min: {y_all_pred_proba.min():.4f}")
    print(f"   Max: {y_all_pred_proba.max():.4f}")
    print(f"   Mean: {y_all_pred_proba.mean():.4f}")
    print(f"   Median: {np.median(y_all_pred_proba):.4f}")
    
    # Уровни риска
    low = (y_all_pred_proba < 0.3).sum()
    med = ((y_all_pred_proba >= 0.3) & (y_all_pred_proba < 0.7)).sum()
    high = (y_all_pred_proba >= 0.7).sum()
    
    print(f"\n🎯 Распределение по уровням риска:")
    print(f"   Low (p<0.3):      {low} ({low/len(df)*100:.1f}%)")
    print(f"   Medium (0.3-0.7): {med} ({med/len(df)*100:.1f}%)")
    print(f"   High (p>0.7):     {high} ({high/len(df)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ ОБУЧЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 80)
    print(f"\n📌 Модель обучена ТОЛЬКО на {len(df)} реальных студентах Softclub")
    print(f"   - Без синтетических данных")
    print(f"   - 645 примеров отчисленных студентов")
    print(f"   - 1028 примеров успешных студентов")


if __name__ == "__main__":
    train_on_real_data()
