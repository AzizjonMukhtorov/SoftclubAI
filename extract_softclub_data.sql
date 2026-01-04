-- =====================================================================
-- SQL ЗАПРОС ДЛЯ ИЗВЛЕЧЕНИЯ ДАННЫХ ИЗ SOFTCLUB CRM
-- Для обучения ML модели предсказания оттока студентов
-- =====================================================================

-- Этот запрос вычисляет 6 features для каждого студента
-- на основе реальных данных из таблиц Softclub CRM

WITH student_stats AS (
    SELECT 
        s."Id" as student_id,
        s."FirstName" || ' ' || s."LastName" as name,
        s."Email" as email,
        
        -- Берем первый курс студента для демонстрации
        (SELECT c."Title" 
         FROM public."StudentGroups" sg2
         JOIN public."Groups" g ON g."Id" = sg2."GroupId"
         JOIN public."Courses" c ON c."Id" = g."CourseId"
         WHERE sg2."StudentId" = s."Id"
         LIMIT 1) as course,
        
        -- =====================================================
        -- FEATURE 1: attendance_rate (Процент посещаемости)
        -- =====================================================
        ROUND(
            (COUNT(CASE WHEN pb."IsAttended" = true THEN 1 END)::numeric / 
             NULLIF(COUNT(pb."Id"), 0) * 100)::numeric,
            2
        ) as attendance_rate,
        
        -- =====================================================
        -- FEATURE 2: homework_completion (Выполнение ДЗ)
        -- Предполагаем что Grade показывает выполнение ДЗ
        -- =====================================================
        ROUND(
            (AVG(CASE WHEN pb."Grade" > 0 THEN pb."Grade" ELSE NULL END))::numeric,
            2
        ) as homework_completion,
        
        -- =====================================================
        -- FEATURE 5: test_avg_score (Средний балл тестов)
        -- Средняя оценка из ProgressBooks
        -- =====================================================
        ROUND(
            (AVG(CASE WHEN pb."Grade" > 0 THEN pb."Grade" ELSE NULL END) / 
             CASE WHEN MAX(pb."Grade") > 100 THEN 100 ELSE NULLIF(MAX(pb."Grade"), 0) END * 100)::numeric,
            2
        ) as test_avg_score,
        
        -- =====================================================
        -- FEATURE 6: communication_activity (Активность)
        -- Количество записей в ProgressBooks с Notes
        -- =====================================================
        COUNT(CASE WHEN pb."Notes" IS NOT NULL AND pb."Notes" != '' THEN 1 END) as communication_activity,
        
        -- =====================================================
        -- FEATURE 7: days_enrolled (Дней с зачисления)
        -- =====================================================
        EXTRACT(DAY FROM 
            CURRENT_DATE - (SELECT MIN(sg3."StartedAt") 
                           FROM public."StudentGroups" sg3 
                           WHERE sg3."StudentId" = s."Id")
        )::int as days_enrolled,
        
        -- =====================================================
        -- FEATURE 8: missed_classes_streak (Пропусков подряд)
        -- Считаем последние пропущенные занятия подряд
        -- =====================================================
        (SELECT COUNT(*) 
         FROM (
             SELECT pb2."IsAttended"
             FROM public."ProgressBooks" pb2
             WHERE pb2."StudentId" = s."Id"
             ORDER BY pb2."Date" DESC
             LIMIT 15
         ) recent_classes
         WHERE recent_classes."IsAttended" = false
        ) as missed_classes_streak,
        
        -- =====================================================
        -- TARGET: churned (Ушел ли студент - 0 или 1)
        -- =====================================================
        CASE 
            WHEN s."Status" = 0 THEN 0  -- Active → остался
            WHEN s."Status" = 1 THEN 1  -- Graduated → остался (закончил)
            WHEN s."Status" = 2 THEN 1  -- Dropped → ушел
            WHEN s."Status" = 3 THEN 1  -- Expelled → ушел
            ELSE 0  -- По умолчанию считаем что остался
        END as churned
        
    FROM public."Students" s
    
    -- Присоединяем ProgressBooks для посещаемости и оценок
    LEFT JOIN public."ProgressBooks" pb ON pb."StudentId" = s."Id"
    
    -- Присоединяем StudentGroups для информации о зачислении
    LEFT JOIN public."StudentGroups" sg ON sg."StudentId" = s."Id"
    
    WHERE s."DeletedAt" = '-infinity'  -- Только не удаленные студенты
    
    GROUP BY s."Id", s."FirstName", s."LastName", s."Email", s."Status"
)

SELECT 
    student_id,
    name,
    email,
    course,
    
    -- 6 FEATURES 
    COALESCE(attendance_rate, 50.0) as attendance_rate,
    COALESCE(homework_completion, 50.0) as homework_completion,
    COALESCE(test_avg_score, 50.0) as test_avg_score,
    COALESCE(communication_activity, 5) as communication_activity,
    COALESCE(days_enrolled, 30) as days_enrolled,
    COALESCE(missed_classes_streak, 0) as missed_classes_streak,
    
    -- TARGET LABEL:
    churned
    
FROM student_stats

WHERE attendance_rate IS NOT NULL  -- Только студенты с данными о посещаемости

ORDER BY student_id

LIMIT 1500;  -- Берем 1500 студентов для обучения

-- =====================================================================
-- ПРИМЕЧАНИЯ:
-- =====================================================================
-- 1. Используем только 6 features 
--
-- 2. Status в таблице Students:
--    0 = Active (активный)
--    1 = Graduated (выпустился)
--    2 = Dropped (отчислился)
--    3 = Expelled (исключен)
--
-- 3. COALESCE используется для замены NULL на дефолтные значения
--
-- 4. Результат можно экспортировать в CSV для обучения модели
-- =====================================================================
