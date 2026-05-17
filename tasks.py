from celery_app import celery_app
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Student, User
from crud import StudentCRUD
import csv
import os

@celery_app.task(bind=True, max_retries=3)
def load_csv_task(self, csv_path: str) -> dict:
    """Фоновая задача: загрузка CSV в БД"""
    try:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Файл не найден: {csv_path}")
        
        db = SessionLocal()
        try:
            crud = StudentCRUD(db)
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                students = [
                    Student(
                        last_name=row['Фамилия'],
                        first_name=row['Имя'],
                        faculty=row['Факультет'],
                        subject=row['Курс'],
                        grade=int(row['Оценка'])
                    )
                    for row in reader
                ]
                db.bulk_save_objects(students)
                db.commit()
                return {"status": "success", "loaded": len(students)}
        finally:
            db.close()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@celery_app.task(bind=True, max_retries=3)
def delete_students_task(self, student_ids: list[int]) -> dict:
    """Фоновая задача: удаление студентов по списку ID"""
    try:
        db = SessionLocal()
        try:
            crud = StudentCRUD(db)
            deleted = 0
            for sid in student_ids:
                if crud.delete(sid):
                    deleted += 1
            db.commit()
            return {"status": "success", "deleted": deleted}
        finally:
            db.close()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)