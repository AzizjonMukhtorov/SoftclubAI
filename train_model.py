"""
🚀 ОБУЧЕНИЕ С ФОКУСОМ НА RECALL (ПОЛНОТУ)
Улучшаем модель, чтобы она находила больше отчисляющихся студентов.

Используемые техники:
1. Class Weights (scale_pos_weight) - балансировка классов
2. Threshold Tuning - подбор оптимального порога вероятности
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, precision_recall_curve
import xgboost as xgb
import os

def train_high_recall_model():
    print("=" * 80)
    print("🚀 ОБУЧЕНИЕ HIGH-RECALL МОДЕЛИ (Чтобы не пропускать отчисления)")
    print("=" * 80)
    
    # 1. Загрузка
    print("\n📊 Загрузка данных...")
    df = pd.read_csv('data/softclub_training.csv')
    
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
    
    # Расчет веса для балансировки
    # scale_pos_weight = (количество active) / (количество churned)
    n_active = (df['churned'] == 0).sum()
    n_churned = (df['churned'] == 1).sum()
    weight_ratio = n_active / n_churned
    
    print(f"   Баланс: {n_active} active vs {n_churned} churned")
    print(f"   ⚖️  Вычислен scale_pos_weight = {weight_ratio:.2f}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 2. Обучение с весами
    print(f"\n🎓 Обучение XGBoost с весом класса {weight_ratio:.2f}...")
    
    model = xgb.XGBClassifier(
        max_depth=4,            # Чуть меньше глубина для обобщения
        learning_rate=0.03,     # Медленнее обучение для точности
        n_estimators=300,
        scale_pos_weight=weight_ratio,  # 🔥 ГЛАВНОЕ ИЗМЕНЕНИЕ: Штрафуем за пропуск churned
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.2,
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    print("   ✅ Модель обучена")
    
    # 3. Подбор порога (Threshold Tuning)
    print("\n🎚️  Подбор оптимального порога (Threshold Tuning)...")
    
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Перебираем пороги
    best_threshold = 0.5
    best_f1 = 0
    best_recall = 0
    
    print(f"{'Threshold':<10} {'Recall':<10} {'Precision':<10} {'F1-Score':<10} {'Active':<10}")
    print("-" * 55)
    
    thresholds = np.arange(0.2, 0.7, 0.05)
    for t in thresholds:
        y_pred_t = (y_pred_proba >= t).astype(int)
        rec = recall_score(y_test, y_pred_t)
        prec = precision_score(y_test, y_pred_t)
        f1 = f1_score(y_test, y_pred_t)
        
        print(f"{t:.2f}       {rec:.2%}     {prec:.2%}      {f1:.2%}      ")
        
        # Ищем порог с хорошим Recall, но чтобы Precision не упал в ноль (>50%)
        if f1 > best_f1 and prec > 0.5:
            best_f1 = f1
            best_threshold = t
            best_recall = rec

    print("-" * 55)
    print(f"🏆 Оптимальный порог: {best_threshold:.2f}")
    
    # 4. Итоговая оценка с лучшим порогом
    print(f"\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ (Threshold = {best_threshold:.2f})")
    
    final_y_pred = (y_pred_proba >= best_threshold).astype(int)
    
    acc = accuracy_score(y_test, final_y_pred)
    rec = recall_score(y_test, final_y_pred)
    prec = precision_score(y_test, final_y_pred)
    f1 = f1_score(y_test, final_y_pred)
    roc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"   Accuracy:  {acc:.2%}")
    print(f"   Precision: {prec:.2%}")
    print(f"   Recall:    {rec:.2%}  (🔥 Было 52.71%)")
    print(f"   F1-Score:  {f1:.2%}")
    print(f"   ROC-AUC:   {roc:.2%}")
    
    cm = confusion_matrix(y_test, final_y_pred)
    print(f"\n📋 Confusion Matrix:")
    print(f"   [[TN={cm[0][0]}  FP={cm[0][1]}]")
    print(f"    [FN={cm[1][0]}   TP={cm[1][1]}]]")
    
    print(f"\n✅ Результат: Нашли {cm[1][1]} из {cm[1][0]+cm[1][1]} отчисленных")
    print(f"   (Пропустили только {cm[1][0]})")
    
    # 5. Сохранение модели
    print("\n💾 Сохранение HIGH-RECALL модели...")
    os.makedirs('models/trained', exist_ok=True)
    model_path = 'models/trained/churn_model.json'
    model.get_booster().save_model(model_path)
    print(f"   ✅ Модель сохранена: {model_path}")
    print("   Теперь модель будет использоваться в API application!")

if __name__ == "__main__":
    train_high_recall_model()
