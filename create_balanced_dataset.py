"""
Создает сбалансированный датасет для обучения ML модели
Комбинирует реальные данные Softclub + синтетические примеры отчисленных студентов
"""
import pandas as pd
import numpy as np

def generate_dropout_students(n_students=1600):
    """
    Генерирует синтетические примеры студентов которые БРОСАЮТ обучение
    Эти студенты имеют плохие показатели (низкая посещаемость, оценки и т.д.)
    """
    print(f"🔧 Генерация {n_students} синтетических студентов-отчисленников...")
    
    students = []
    np.random.seed(42)
    
    # Типы "плохих" студентов которые бросают
    dropout_types = [
        'low_attendance',      # Низкая посещаемость
        'poor_performance',    # Плохая успеваемость
        'payment_issues',      # Финансовые проблемы (мы не используем, но для разнообразия)
        'lost_motivation',     # Потерял мотивацию
        'no_communication',    # Не выходит на связь
    ]
    
    for i in range(n_students):
        dropout_type = np.random.choice(dropout_types)
        
        if dropout_type == 'low_attendance':
            # Студент с очень низкой посещаемостью
            attendance_rate = np.random.uniform(0, 40)
            homework_completion = np.random.uniform(0, 50)
            test_avg_score = np.random.uniform(20, 60)
            communication_activity = np.random.randint(0, 5)
            days_enrolled = np.random.randint(10, 90)
            missed_classes_streak = np.random.randint(5, 15)
            
        elif dropout_type == 'poor_performance':
            # Студент с плохой успеваемостью
            attendance_rate = np.random.uniform(40, 70)
            homework_completion = np.random.uniform(0, 40)
            test_avg_score = np.random.uniform(0, 40)
            communication_activity = np.random.randint(0, 8)
            days_enrolled = np.random.randint(20, 120)
            missed_classes_streak = np.random.randint(2, 10)
            
        elif dropout_type == 'payment_issues':
            # Студент с финансовыми проблемами (учится хорошо, но не может платить)
            attendance_rate = np.random.uniform(60, 85)
            homework_completion = np.random.uniform(50, 80)
            test_avg_score = np.random.uniform(50, 75)
            communication_activity = np.random.randint(5, 15)
            days_enrolled = np.random.randint(30, 90)
            missed_classes_streak = np.random.randint(3, 12)
            
        elif dropout_type == 'lost_motivation':
            # Студент потерял мотивацию (начал хорошо, потом резко упал)
            attendance_rate = np.random.uniform(30, 60)
            homework_completion = np.random.uniform(20, 50)
            test_avg_score = np.random.uniform(30, 55)
            communication_activity = np.random.randint(0, 5)
            days_enrolled = np.random.randint(40, 150)
            missed_classes_streak = np.random.randint(7, 15)
            
        else:  # no_communication
            # Студент перестал выходить на связь
            attendance_rate = np.random.uniform(10, 50)
            homework_completion = np.random.uniform(0, 30)
            test_avg_score = np.random.uniform(15, 50)
            communication_activity = 0  # Нет коммуникации!
            days_enrolled = np.random.randint(15, 80)
            missed_classes_streak = np.random.randint(8, 15)
        
        students.append({
            'student_id': f'SYNTH_{i+10000}',
            'name': f'Synthetic Student {i+1}',
            'email': f'synthetic{i+1}@example.com',
            'attendance_rate': round(attendance_rate, 2),
            'homework_completion': round(homework_completion, 2),
            'test_avg_score': round(test_avg_score, 2),
            'communication_activity': communication_activity,
            'days_enrolled': days_enrolled,
            'missed_classes_streak': missed_classes_streak,
            'churned': 1  # ВСЕ синтетические = отчисленные
        })
        
        if (i + 1) % 500 == 0:
            print(f"   Сгенерировано {i + 1} студентов...")
    
    return pd.DataFrame(students)


def generate_active_students(n_students=1625):
    """
    Генерирует синтетические примеры АКТИВНЫХ студентов
    Эти студенты имеют хорошие показатели (высокая посещаемость, оценки и т.д.)
    """
    print(f"🔧 Генерация {n_students} синтетических активных студентов...")
    
    students = []
    np.random.seed(43)  # Другой seed
    
    for i in range(n_students):
        # Хороший студент
        attendance_rate = np.random.uniform(70, 100)
        homework_completion = np.random.uniform(60, 100)
        test_avg_score = np.random.uniform(60, 100)
        communication_activity = np.random.randint(5, 25)
        days_enrolled = np.random.randint(30, 365)
        missed_classes_streak = np.random.randint(0, 3)
        
        students.append({
            'student_id': f'SYNTH_ACTIVE_{i+20000}',
            'name': f'Active Student {i+1}',
            'email': f'active{i+1}@example.com',
            'attendance_rate': round(attendance_rate, 2),
            'homework_completion': round(homework_completion, 2),
            'test_avg_score': round(test_avg_score, 2),
            'communication_activity': communication_activity,
            'days_enrolled': days_enrolled,
            'missed_classes_streak': missed_classes_streak,
            'churned': 0  # ВСЕ синтетические активные = НЕ отчисленные
        })
        
        if (i + 1) % 500 == 0:
            print(f"   Сгенерировано {i + 1} студентов...")
    
    return pd.DataFrame(students)


def main():
    print("=" * 80)
    print("🚀 СОЗДАНИЕ СБАЛАНСИРОВАННОГО ДАТАСЕТА")
    print("=" * 80)
    
    # Загружаем реальные данные Softclub
    print("\n📊 Загрузка реальных данных Softclub...")
    real_df = pd.read_csv('data/softclub_training.csv')
    print(f"   ✅ Загружено {len(real_df)} реальных студентов")
    print(f"      - churned=0: {(real_df['churned'] == 0).sum()}")
    print(f"      - churned=1: {(real_df['churned'] == 1).sum()}")
    
    # Генерируем синтетические отчисленные
    n_synthetic_dropout = 1600  # Добавляем примеры отчисленных
    synthetic_dropout_df = generate_dropout_students(n_synthetic_dropout)
    print(f"   ✅ Сгенерировано {len(synthetic_dropout_df)} синтетических отчисленников")
    
    # Генерируем синтетические активные
    n_synthetic_active = 1625  # Добавляем примеры активных (для баланса)
    synthetic_active_df = generate_active_students(n_synthetic_active)
    print(f"   ✅ Сгенерировано {len(synthetic_active_df)} синтетических активных")
    
    # Комбинируем
    print("\n🔗 Комбинирование датасетов...")
    combined_df = pd.concat([real_df, synthetic_dropout_df, synthetic_active_df], ignore_index=True)
    
    # Перемешиваем
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Сохраняем
    output_file = 'data/training_data_balanced.csv'
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Готово!")
    print(f"📁 Сохранено: {output_file}")
    print(f"📊 Всего студентов: {len(combined_df)}")
    
    # Финальная статистика
    print(f"\n📈 Финальное распределение:")
    print(f"   churned=0 (активные/закончили): {(combined_df['churned'] == 0).sum()}")
    print(f"   churned=1 (отчислились): {(combined_df['churned'] == 1).sum()}")
    
    # Процентное соотношение
    total = len(combined_df)
    pct_active = (combined_df['churned'] == 0).sum() / total * 100
    pct_churned = (combined_df['churned'] == 1).sum() / total * 100
    
    print(f"\n   Баланс: {pct_active:.1f}% активных vs {pct_churned:.1f}% отчисленных")
    
    print("\n" + "=" * 80)
    print("🎯 Сбалансированный датасет готов для обучения модели!")
    print("=" * 80)


if __name__ == "__main__":
    main()
