import csv
from sqlalchemy.orm import Session
from models import Student, engine, SessionLocal

def load_students_from_csv(csv_file: str):
    """Загружает данные из CSV в базу данных"""
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with Session(engine) as session:
            students = []
            for row in reader:
                student = Student(
                    last_name=row['Фамилия'],
                    first_name=row['Имя'],
                    faculty=row['Факультет'],
                    subject=row['Курс'],  # В CSV колонка "Курс" содержит предметы
                    grade=int(row['Оценка'])
                )
                students.append(student)
            
            session.bulk_save_objects(students)
            session.commit()
            print(f"✅ Загружено {len(students)} студентов")

if __name__ == "__main__":
    load_students_from_csv("students.csv")