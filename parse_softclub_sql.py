"""
Парсер SQL дампа Softclub для извлечения данных студентов
Извлекает данные из softclub.sql и создает CSV с 6 features для ML обучения
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re

def parse_copy_data(filename, table_name):
    """Парсит COPY ... FROM stdin данные из SQL файла"""
    print(f"📊 Парсинг таблицы {table_name}...")
    
    data = []
    in_copy = False
    columns = []
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            # Начало COPY блока
            if f'COPY public."{table_name}"' in line:
                # Извлекаем названия колонок
                match = re.search(r'\((.*?)\)', line)
                if match:
                    columns = [col.strip().strip('"') for col in match.group(1).split(',')]
                in_copy = True
                continue
            
            # Конец COPY блока
            if in_copy and line.strip() == '\\.':
                in_copy = False
                continue
            
            # Парсим строку данных
            if in_copy and line.strip():
                try:
                    # Разделяем по табуляции
                    values = line.strip().split('\t')
                    
                    # Преобразуем \N в None
                    values = [None if v == '\\N' else v for v in values]
                    
                    # Создаем словарь
                    if len(values) == len(columns):
                        row = dict(zip(columns, values))
                        data.append(row)
                except Exception as e:
                    # Игнорируем ошибочные строки
                    continue
    
    df = pd.DataFrame(data)
    print(f"   ✅ Загружено {len(df)} записей")
    return df


def calculate_features(students_df, progress_df, student_groups_df):
    """Вычисляет 6 ML features для каждого студента"""
    print("\n🔧 Вычисление features...")
    
    features_list = []
    
    for idx, student in students_df.iterrows():
        student_id = student['Id']
        
        # Фильтруем прогресс этого студента
        student_progress = progress_df[progress_df['StudentId'] == student_id]
        
        if len(student_progress) == 0:
            # Пропускаем студентов без данных о посещаемости
            continue
        
        # FEATURE 1: attendance_rate
        attended = student_progress['IsAttended'].apply(lambda x: x == 't' or x == True).sum()
        total = len(student_progress)
        attendance_rate = round((attended / total * 100) if total > 0 else 50.0, 2)
        
        # FEATURE 2: homework_completion (используем Grade как прокси)
        grades = student_progress['Grade'].apply(pd.to_numeric, errors='coerce')
        homework_completion = round(grades.mean() if not grades.isna().all() else 50.0, 2)
        
        # FEATURE 3: test_avg_score (нормализуем оценки к 0-100)
        max_grade = grades.max() if not grades.isna().all() else 100
        if max_grade > 0:
            test_avg_score = round((grades.mean() / max_grade * 100) if not grades.isna().all() else 50.0, 2)
        else:
            test_avg_score = 50.0
        
        # FEATURE 4: communication_activity (количество записей с Notes)
        communication_activity = len(student_progress[student_progress['Notes'].notna()])
        
        # FEATURE 5: days_enrolled
        student_group = student_groups_df[student_groups_df['StudentId'] == student_id]
        if len(student_group) > 0:
            try:
                started_at = pd.to_datetime(student_group.iloc[0]['StartedAt'])
                days_enrolled = max((datetime.now() - started_at).days, 1)
            except:
                days_enrolled = 30
        else:
            days_enrolled = 30
        
        # FEATURE 6: missed_classes_streak (последние пропуски подряд)
        recent_attendance = student_progress.sort_values('Date', ascending=False).head(15)
        missed_streak = 0
        for _, record in recent_attendance.iterrows():
            if record['IsAttended'] == 'f' or record['IsAttended'] == False:
                missed_streak += 1
            else:
                break
        
        # TARGET: churned - используем StudentGroupStatus из StudentGroups!
        # StudentGroupStatus:
        #   0 = Active в группе
        #   1 = Graduated (закончил successfully)
        #   2 = Dropped/Expelled (ОТЧИСЛЕН!) ← ЭТО НАША ЦЕЛЬ!
        #   3 = Unknown/Other
        
        churned = 0  # По умолчанию
        
        # Проверяем StudentGroupStatus
        student_group = student_groups_df[student_groups_df['StudentId'] == student_id]
        if len(student_group) > 0:
            try:
                # Берем последний статус студента (если несколько групп)
                last_group_status = int(student_group.iloc[-1]['StudentGroupStatus'])
                # Статус 2 = отчислен!
                churned = 1 if last_group_status == 2 else 0
            except:
                churned = 0
        else:
            # Если нет в StudentGroups, используем Students.Status как fallback
            try:
                status = int(student['Status'])
                churned = 1 if status in [2, 3] else 0
            except:
                churned = 0
        
        features_list.append({
            'student_id': student_id,
            'name': f"{student.get('FirstName', '')} {student.get('LastName', '')}".strip(),
            'email': student.get('Email', ''),
            'attendance_rate': attendance_rate,
            'homework_completion': homework_completion,
            'test_avg_score': test_avg_score,
            'communication_activity': communication_activity,
            'days_enrolled': days_enrolled,
            'missed_classes_streak': missed_streak,
            'churned': churned
        })
        
        if len(features_list) % 100 == 0:
            print(f"   Обработано {len(features_list)} студентов...")
    
    return pd.DataFrame(features_list)


def main():
    print("=" * 80)
    print("🚀 ПАРСИНГ SOFTCLUB SQL ДАМПА")
    print("=" * 80)
    
    # Парсим таблицы
    students_df = parse_copy_data('softclub.sql', 'Students')
    progress_df = parse_copy_data('softclub.sql', 'ProgressBooks')
    student_groups_df = parse_copy_data('softclub.sql', 'StudentGroups')
    
    # Вычисляем features
    features_df = calculate_features(students_df, progress_df, student_groups_df)
    
    # Сохраняем CSV
    output_file = 'data/softclub_training.csv'
    features_df.to_csv(output_file, index=False)
    
    # Используем ВСЕ студенты (без ограничения)
    print(f"\n✅ Готово!")
    print(f"📁 Сохранено: {output_file}")
    print(f"📊 Всего студентов: {len(features_df)}")
    
    # Статистика
    print(f"\n📈 Распределение:")
    print(f"   Остались (churned=0): {(features_df['churned'] == 0).sum()}")
    print(f"   Ушли (churned=1): {(features_df['churned'] == 1).sum()}")
    
    print("\n" + "=" * 80)
    print("🎯 Данные готовы для обучения модели!")
    print("=" * 80)


if __name__ == "__main__":
    main()
