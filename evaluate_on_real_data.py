"""
ЧЕСТНАЯ ОЦЕНКА ML МОДЕЛИ НА РЕАЛЬНЫХ ДАННЫХ ИЗ POSTGRESQL

Модель обучена на 15,000 синтетических данных (это OK)
НО теперь тестируем на РЕАЛЬНЫХ студентах из БД!
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import xgboost as xgb
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from app.db.database import SessionLocal
from app.db.models import Student as DBStudent


def evaluate_on_real_data():
    """Оценка модели на РЕАЛЬНЫХ студентах из PostgreSQL"""
    
    print("=" * 80)
    print("🎯 ЧЕСТНАЯ ОЦЕНКА НА РЕАЛЬНЫХ ДАННЫХ ИЗ POSTGRESQL")
    print("=" * 80)
    
    # Загружаем модель (обучена на 15,000 синтетических)
    print("\n🔧 Загрузка модели...")
    model = xgb.XGBClassifier()
    model.load_model('models/trained/churn_model.json')
    print("   ✅ Модель обучена на 15,000 синтетических примерах")
    
    # Получаем РЕАЛЬНЫХ студентов из PostgreSQL
    print("\n📊 Получение РЕАЛЬНЫХ студентов из БД...")
    db = SessionLocal()
    
    try:
        real_students = db.query(DBStudent).all()
        print(f"   ✅ Получено {len(real_students)} студентов из crm-softclub БД")
        
        if len(real_students) == 0:
            print("   ❌ В БД нет студентов!")
            return
        
        # Подготовка данных
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
        
        X_real = []
        y_true = []  # Настоящие метки (определяем вручную)
        student_names = []
        
        print("\n📋 Студенты из БД:")
        print(f"{'ID':<4} {'Имя':<20} {'Посещ':<7} {'ДЗ':<7} {'Delay':<6} {'Ожидаемый Risk'}")
        print("-" * 80)
        
        for s in real_students:
            # Готовим features
            features = [
                s.attendance_rate,
                s.homework_completion,
                s.payment_delays,
                s.days_since_last_payment,
                s.test_avg_score,
                s.communication_activity,
                s.days_enrolled,
                s.missed_classes_streak
            ]
            X_real.append(features)
            
            # Определяем ОЖИДАЕМЫЙ risk вручную на основе данных
            if s.attendance_rate < 45 and s.homework_completion < 45:
                expected_risk = 2  # High Risk
                risk_name = "High"
            elif s.attendance_rate < 70 or s.homework_completion < 70:
                expected_risk = 1  # Medium Risk
                risk_name = "Medium"
            else:
                expected_risk = 0  # Low Risk
                risk_name = "Low"
            
            y_true.append(expected_risk)
            student_names.append(s.name)
            
            print(f"{s.id:<4} {s.name:<20} {s.attendance_rate:6.1f}% {s.homework_completion:6.1f}% {s.payment_delays:<6} {risk_name}")
        
        X_real = np.array(X_real)
        y_true = np.array(y_true)
        
        # Делаем предсказания
        print("\n🤖 Предсказания модели на РЕАЛЬНЫХ данных...")
        y_pred = model.predict(X_real)
        y_proba = model.predict_proba(X_real)
        
        # Показываем предсказания
        print("\n📊 РЕЗУЛЬТАТЫ:")
        print(f"{'ID':<4} {'Имя':<20} {'Ожидаемый':<12} {'ML Прогноз':<12} {'Confidence':<11} {'✓'}")
        print("-" * 80)
        
        correct = 0
        for i, (name, true_label, pred_label, proba) in enumerate(zip(student_names, y_true, y_pred, y_proba)):
            true_name = {0: 'Low', 1: 'Medium', 2: 'High'}[true_label]
            pred_name = {0: 'Low', 1: 'Medium', 2: 'High'}[pred_label]
            confidence = proba[pred_label] * 100
            
            is_correct = "✅" if true_label == pred_label else "❌"
            if true_label == pred_label:
                correct += 1
            
            print(f"{i+1:<4} {name:<20} {true_name:<12} {pred_name:<12} {confidence:>6.1f}%     {is_correct}")
        
        accuracy = correct / len(y_true)
        print("\n" + "=" * 80)
        print(f"📊 ОБЩАЯ ТОЧНОСТЬ: {correct}/{len(y_true)} = {accuracy:.2%}")
        print("=" * 80)
        
        # Метрики (если есть хотя бы по 2 примера каждого класса)
        unique_true = np.unique(y_true)
        unique_pred = np.unique(y_pred)
        
        if len(unique_true) >= 2:
            print("\n📈 ДЕТАЛЬНЫЕ МЕТРИКИ:\n")
            
            # Classification Report
            target_names = ['Low Risk', 'Medium Risk', 'High Risk']
            # Используем только классы которые есть в данных
            labels_present = sorted(list(set(y_true) | set(y_pred)))
            names_present = [target_names[i] for i in labels_present]
            
            print(classification_report(y_true, y_pred, labels=labels_present, 
                                       target_names=names_present, zero_division=0))
            
            print("\n🔢 CONFUSION MATRIX:")
            cm = confusion_matrix(y_true, y_pred, labels=labels_present)
            
            print(f"\n      Predicted: ", end="")
            for label in labels_present:
                print(f"{target_names[label]:>8s}", end="")
            print()
            
            for i, true_label in enumerate(labels_present):
                print(f"   {target_names[true_label]:12s}", end="")
                for j in range(len(labels_present)):
                    print(f"{cm[i,j]:>8d}", end="")
                print()
            
            # Precision, Recall по классам
            print("\n📊 МЕТРИКИ ПО КЛАССАМ:")
            for label in labels_present:
                if (y_true == label).sum() > 0:
                    prec = precision_score(y_true, y_pred, labels=[label], average='macro', zero_division=0)
                    rec = recall_score(y_true, y_pred, labels=[label], average='macro', zero_division=0) 
                    f1 = f1_score(y_true, y_pred, labels=[label], average='macro', zero_division=0)
                    
                    print(f"\n{target_names[label]}:")
                    print(f"  Precision: {prec:.2%}")
                    print(f"  Recall:    {rec:.2%}")
                    print(f"  F1-Score:  {f1:.2%}")
        
        # Итоговая оценка
        print("\n" + "=" * 80)
        print("💡 ВЫВОДЫ:")
        print("=" * 80)
        print(f"\n✅ Модель обучена на: 15,000 синтетических примерах")
        print(f"✅ Протестирована на: {len(y_true)} РЕАЛЬНЫХ студентах из PostgreSQL")
        print(f"📊 Точность на реальных данных: {accuracy:.1%}")
        
        if accuracy >= 0.8:
            print("\n🎯 Оценка: ⭐⭐⭐⭐ Отлично для реальных данных!")
        elif accuracy >= 0.7:
            print("\n🎯 Оценка: ⭐⭐⭐ Хорошо (норма для churn prediction)")
        elif accuracy >= 0.6:
            print("\n🎯 Оценка: ⭐⭐ Средне")
        else:
            print("\n🎯 Оценка: ⭐ Нужно улучшение")
        
        # High Risk detection (самое важное)
        high_risk_true = (y_true == 2).sum()
        high_risk_pred_correct = ((y_true == 2) & (y_pred == 2)).sum()
        
        if high_risk_true > 0:
            high_risk_recall = high_risk_pred_correct / high_risk_true
            print(f"\n💡 High Risk Recall: {high_risk_recall:.1%} (нашли {high_risk_pred_correct}/{high_risk_true})")
            print("   Это главная метрика для бизнеса!")
        
        print("\n" + "=" * 80)
        
    finally:
        db.close()


if __name__ == "__main__":
    evaluate_on_real_data()
