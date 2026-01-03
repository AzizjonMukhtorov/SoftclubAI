import random
import pandas as pd
import numpy as np
from typing import List, Dict


def generate_realistic_student_profile(risk_category: str) -> Dict:
    """
    Генерирует реалистичный профиль студента на основе категории риска
    
    Args:
        risk_category: 'low', 'medium', или 'high'
    
    Returns:
        Словарь с характеристиками студента
    """
    
    if risk_category == 'low':
        # Успешные студенты - сильные корреляции
        attendance = np.random.beta(8, 2) * 100  # Смещено к 80-100%
        homework = attendance + np.random.normal(0, 5)  # Коррелирует с посещаемостью
        homework = np.clip(homework, 70, 100)
        
        # Тесты зависят от посещаемости и ДЗ
        test_score = (attendance * 0.5 + homework * 0.5) + np.random.normal(0, 7)
        test_score = np.clip(test_score, 70, 100)
        
        payment_delays = np.random.choice([0, 1], p=[0.9, 0.1])
        days_since_payment = np.random.randint(0, 15) if payment_delays == 0 else np.random.randint(15, 30)
        
        communication = np.random.randint(10, 25)  # Активные
        missed_streak = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
        days_enrolled = np.random.randint(30, 250)
        
        risk_label = 0  # Low Risk
        
    elif risk_category == 'medium':
        # Студенты "на грани" - проблемы в некоторых областях
        attendance = np.random.beta(4, 4) * 100  # Середина 40-80%
        
        # Несколько сценариев для medium risk:
        scenario = np.random.choice(['lazy', 'financial', 'struggling'])
        
        if scenario == 'lazy':  # Ленивый но способный
            homework = np.clip(attendance - 20 + np.random.normal(0, 10), 30, 70)
            test_score = np.clip(attendance + 10 + np.random.normal(0, 10), 50, 85)
            payment_delays = np.random.randint(0, 2)
            communication = np.random.randint(3, 8)
            
        elif scenario == 'financial':  # Финансовые проблемы
            homework = np.clip(attendance + np.random.normal(0, 10), 50, 85)
            test_score = np.clip(homework + np.random.normal(0, 8), 50, 80)
            payment_delays = np.random.randint(2, 5)
            communication = np.random.randint(5, 15)
            
        else:  # 'struggling' - борется с материалом
            homework = np.clip(attendance - 15 + np.random.normal(0, 10), 30, 65)
            test_score = np.clip(homework - 10 + np.random.normal(0, 10), 35, 65)
            payment_delays = np.random.randint(0, 3)
            communication = np.random.randint(2, 10)
        
        days_since_payment = np.random.randint(0, 45)
        missed_streak = np.random.randint(1, 5)
        days_enrolled = np.random.randint(20, 200)
        
        risk_label = 1  # Medium Risk
        
    else:  # high risk
        # Проблемные студенты - ясные красные флаги
        attendance = np.random.beta(2, 5) * 100  # Смещено к 20-50%
        
        # Высокий риск может быть из-за разных причин:
        cause = np.random.choice(['disengaged', 'overwhelmed', 'financial_crisis'])
        
        if cause == 'disengaged':  # Потерял интерес
            homework = np.clip(attendance - 15 + np.random.normal(0, 8), 10, 50)
            test_score = np.clip(homework - 5 + np.random.normal(0, 10), 20, 55)
            payment_delays = np.random.randint(1, 6)
            communication = np.random.randint(0, 3)
            missed_streak = np.random.randint(3, 10)
            
        elif cause == 'overwhelmed':  # Не справляется
            homework = np.clip(attendance - 10 + np.random.normal(0, 10), 15, 50)
            test_score = np.clip(homework - 15 + np.random.normal(0, 8), 15, 45)
            payment_delays = np.random.randint(0, 4)
            communication = np.random.randint(1, 5)
            missed_streak = np.random.randint(2, 8)
            
        else:  # 'financial_crisis'
            homework = np.clip(attendance + np.random.normal(0, 15), 20, 60)
            test_score = np.clip(homework + np.random.normal(0, 10), 25, 60)
            payment_delays = np.random.randint(4, 10)
            communication = np.random.randint(0, 6)
            missed_streak = np.random.randint(2, 7)
        
        days_since_payment = np.random.randint(30, 90)
        days_enrolled = np.random.randint(10, 150)
        
        risk_label = 2  # High Risk
    
    return {
        'attendance_rate': round(float(attendance), 2),
        'homework_completion': round(float(homework), 2),
        'payment_delays': int(payment_delays),
        'days_since_last_payment': int(days_since_payment),
        'test_avg_score': round(float(test_score), 2),
        'communication_activity': int(communication),
        'days_enrolled': int(days_enrolled),
        'missed_classes_streak': int(missed_streak),
        'risk_label': risk_label
    }


def generate_realistic_training_data(n_samples: int = 10000, 
                                     low_ratio: float = 0.45,
                                     medium_ratio: float = 0.30,
                                     high_ratio: float = 0.25) -> pd.DataFrame:
    """
    Генерирует реалистичные тренировочные данные с правильными распределениями
    
    Args:
        n_samples: Количество примеров (рекомендуется 10000+)
        low_ratio: Доля Low Risk студентов
        medium_ratio: Доля Medium Risk студентов  
        high_ratio: Доля High Risk студентов
    
    Returns:
        DataFrame с реалистичными данными
    """
    print(f"🎯 Генерация {n_samples} РЕАЛИСТИЧНЫХ примеров...")
    
    # Рассчитываем количество для каждой категории
    n_low = int(n_samples * low_ratio)
    n_medium = int(n_samples * medium_ratio)
    n_high = n_samples - n_low - n_medium
    
    data = []
    
    # Генерируем Low Risk студентов
    print(f"   ✅ Low Risk: {n_low} студентов...")
    for _ in range(n_low):
        data.append(generate_realistic_student_profile('low'))
    
    # Генерируем Medium Risk студентов
    print(f"   ⚠️  Medium Risk: {n_medium} студентов...")
    for _ in range(n_medium):
        data.append(generate_realistic_student_profile('medium'))
    
    # Генерируем High Risk студентов
    print(f"   🔴 High Risk: {n_high} студентов...")
    for _ in range(n_high):
        data.append(generate_realistic_student_profile('high'))
    
    # Перемешиваем данные
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"\\n✅ Сгенерировано {len(df)} примеров с реалистичными корреляциями!")
    
    return df


if __name__ == "__main__":
    # Тест генератора
    df = generate_realistic_training_data(n_samples=1000)
    
    print("\\n📊 Распределение классов:")
    print(df['risk_label'].value_counts().sort_index())
    
    print("\\n📈 Статистика по классам:")
    for label in [0, 1, 2]:
        risk_name = {0: 'Low', 1: 'Medium', 2: 'High'}[label]
        subset = df[df['risk_label'] == label]
        print(f"\\n{risk_name} Risk:")
        print(f"  Посещаемость: {subset['attendance_rate'].mean():.1f}% ± {subset['attendance_rate'].std():.1f}")
        print(f"  ДЗ: {subset['homework_completion'].mean():.1f}% ± {subset['homework_completion'].std():.1f}")
        print(f"  Задержки оплаты: {subset['payment_delays'].mean():.1f}")
