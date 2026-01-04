"""
Загружает демо-данные в БД из CSV
"""
from app.db.database import SessionLocal
from app.db.models import Student
import csv

# Данные студентов
students_data = """student_id,student_name,course_title,attendance_rate,homework_completion,test_avg_score,communication_activity,days_enrolled,missed_classes_streak,dropped_out
2000,Farrukh Sobirov,Python,38.54,21.12,48.41,8,21,14,1
2001,Nigina Karimova,SQL,41.19,30.09,48.24,8,25,14,1
2002,Jamshed Aliev,Data Science,41.32,52.83,52.53,7,74,12,1
2003,Madina Rahmonova,Machine Learning,38.06,29.0,51.93,3,63,14,1
2004,Rustam Nabiev,DevOps,46.98,37.22,58.58,2,45,10,1
2005,Daler Sharipov,Angular,39.96,26.6,51.77,1,90,11,1
2006,Zarina Yusupova,Flask,36.21,43.21,44.97,1,83,13,1
2007,Parviz Saidov,Mobile Development,25.34,25.03,34.12,0,59,12,1
2008,Manizha Davlatova,Cybersecurity,47.39,35.48,51.3,2,48,11,1
2009,Sheroz Tursunov,Java,35.64,25.27,30.09,5,289,11,1
2010,Aziz Nematov,JavaScript,35.86,35.73,30.09,2,43,10,1
2011,Malika Hakimova,Graphic Design,38.59,48.11,56.04,5,118,11,1
2012,Behruz Holmatov,MongoDB,53.78,27.88,43.57,2,19,10,1
2013,Nilufar Boboeva,JavaScript,36.08,25.25,40.17,2,239,14,1
2014,Khusrav Mirzoev,Mobile Development,39.84,39.0,34.24,1,46,13,1
2015,Tahmina Rajabova,Django,44.87,31.87,43.79,6,261,11,1
2016,Komron Zokirov,Vue.js,47.13,39.14,36.92,2,218,13,1
2017,Firuz Latipov,Cybersecurity,40.54,39.85,48.26,3,129,7,1
2018,Sabina Umarova,Graphic Design,52.43,35.96,48.39,5,139,9,1
2019,Umedjon Qodirov,Python,46.45,22.64,40.89,6,238,9,1
2020,Sukhrob Nuraliev,DevOps,76.61,47.17,64.88,15,245,7,1
2021,Shahnoza Ismoilova,Data Science,73.81,61.15,68.96,8,123,5,0
2022,Alisher Vakhidov,SQL,63.83,63.47,74.49,20,234,7,1
2023,Ilhom Juraev,Data Science,60.84,73.6,57.05,5,132,5,1
2024,Mavzuna Akramova,Graphic Design,77.2,69.75,71.37,8,125,4,0
2025,Akmal Rasulov,Angular,78.48,64.7,68.5,16,157,8,0
2026,Ganjina Nosirova,Angular,61.52,59.08,59.41,10,27,2,1
2027,Samir Shukurov,Mobile Development,65.76,68.63,69.1,13,164,5,0
2028,Hassan Iskandarov,Web Development,78.55,55.95,62.43,18,161,8,0
2029,Firdavs Ashurov,Vue.js,78.44,57.71,77.28,12,206,5,1
2030,Zafar Tuychiev,SQL,61.65,69.07,64.11,10,108,7,0
2031,Sitora Ahmedova,Web Development,62.54,62.19,67.45,3,49,1,0
2032,Dilshod Mahmudov,JavaScript,63.68,52.46,63.87,9,67,2,1
2033,Rukhshona Saidova,UX/UI Design,53.98,49.62,52.13,9,46,3,1
2034,Iskandar Sadykov,MongoDB,60.49,64.15,73.21,12,133,3,1
2035,Faridun Karimov,Graphic Design,91.2,76.77,67.3,11,236,1,0
2036,Noziya Kurbonova,SQL,81.63,74.68,65.5,18,283,1,0
2037,Husniddin Rahimov,Angular,94.92,77.32,87.75,14,249,1,0
2038,Nizom Dustov,Mobile Development,83.87,94.01,71.99,22,244,2,0
2039,Fatima Gafurova,DevOps,94.78,90.74,71.37,24,291,0,0
2040,Yusuf Oripov,Data Science,75.3,90.8,81.78,12,194,1,0
2041,Laylo Khamidova,Machine Learning,86.64,92.56,98.91,16,286,0,0
2042,Ravshan Boltayev,JavaScript,94.89,85.61,80.11,18,175,2,0
2043,Aminjon Salimov,HTML/CSS,92.48,71.86,66.93,21,295,1,0
2044,Hasan Qahhorov,Data Science,93.43,95.05,88.22,28,284,0,0
2045,Zayd Abdulloev,Node.js,75.91,61.29,31.76,7,21,1,0
2046,Saidmurod Kholov,Java,82.05,80.2,73.54,0,226,3,0
2047,Yasin Fayzullaev,DevOps,63.04,46.43,65.03,3,357,6,1
2048,Hamza Muminov,HTML/CSS,74.68,69.78,88.08,0,149,2,0
2049,Ranodushanbe Tariqova,MongoDB,31.04,89.61,81.09,6,282,5,1"""

def load_data():
    print("=" * 60)
    print("📥 ЗАГРУЗКА ДЕМО-ДАННЫХ В БД")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Очистка существующих данных
        print("\n🗑️  Очистка старых данных...")
        db.query(Student).delete()
        db.commit()
        print("   ✅ Старые данные удалены")
        
        # Парсинг CSV
        print("\n📊 Загрузка новых студентов...")
        reader = csv.DictReader(students_data.strip().split('\n'))
        
        count = 0
        for row in reader:
            student = Student(
                id=int(row['student_id']),
                name=row['student_name'],
                email=f"{row['student_name'].lower().replace(' ', '.')}@softclub.tj",
                course=row['course_title'],
                phone_number=f"+992 900 {str(row['student_id'])[-3:]} {str(row['student_id'])[-2:]} 00",
                attendance_rate=float(row['attendance_rate']),
                homework_completion=float(row['homework_completion']),
                test_avg_score=float(row['test_avg_score']),
                communication_activity=int(row['communication_activity']),
                days_enrolled=int(row['days_enrolled']),
                missed_classes_streak=int(row['missed_classes_streak'])
            )
            db.add(student)
            count += 1
        
        db.commit()
        print(f"   ✅ Загружено {count} студентов")
        
        # Статистика
        total = db.query(Student).count()
        print(f"\n📊 Всего в БД: {total} студентов")
        
        print("\n" + "=" * 60)
        print("✅ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Ошибка: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_data()
