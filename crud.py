from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Student
import csv
import io
from typing import List, Tuple, Optional

class StudentCRUD:
    def __init__(self, db: Session):
        self.db = db

    # 🔹 INSERT
    def create(self, data: dict) -> Student:
        new_student = Student(**data)
        self.db.add(new_student)
        self.db.commit()
        self.db.refresh(new_student)  # Возвращаем объект с заполненным id
        return new_student

    # 🔹 SELECT (по ID)
    def get_by_id(self, student_id: int) -> Optional[Student]:
        return self.db.query(Student).filter(Student.id == student_id).first()

    #  SELECT (все записи)
    def get_all(self) -> List[Student]:
        return self.db.query(Student).all()

    # 🔹 UPDATE
    def update(self, student_id: int, update_data: dict) -> Optional[Student]:
        student = self.get_by_id(student_id)
        if not student:
            return None
        for key, value in update_data.items():
            setattr(student, key, value)  # Безопасно обновляем только переданные поля
        self.db.commit()
        self.db.refresh(student)
        return student

    # 🔹 DELETE
    def delete(self, student_id: int) -> bool:
        student = self.get_by_id(student_id)
        if not student:
            return False
        self.db.delete(student)
        self.db.commit()
        return True

    # 📊 Запрос 1: Студенты по факультету
    def get_by_faculty(self, faculty: str) -> List[Student]:
        return self.db.query(Student).filter(Student.faculty == faculty).all()

    # 📊 Запрос 2: Уникальные курсы (предметы)
    def get_unique_courses(self) -> List[str]:
        # distinct() убирает дубли, возвращаем только названия
        return [row[0] for row in self.db.query(Student.subject).distinct().all()]

    # 📊 Запрос 3: Студенты по курсу с оценкой < 30
    def get_low_grades(self, course: str, threshold: int = 30) -> List[Student]:
        return self.db.query(Student).filter(
            Student.subject == course,
            Student.grade < threshold
        ).all()

    # 📊 Запрос 4: Средний балл по факультету
    def get_avg_grade_by_faculty(self) -> List[Tuple[str, float]]:
        # group_by + func.avg = чистая SQL-агрегация
        return self.db.query(
            Student.faculty,
            func.avg(Student.grade).label("avg_grade")
        ).group_by(Student.faculty).all()

    # 🎁 Бонус: Экспорт в CSV (в памяти, без записи на диск)
    def export_to_csv(self) -> str:
        students = self.get_all()
        output = io.StringIO()
        writer = csv.writer(output)
        # Заголовки как в исходнике
        writer.writerow(["Фамилия", "Имя", "Факультет", "Курс", "Оценка"])
        for s in students:
            writer.writerow([s.last_name, s.first_name, s.faculty, s.subject, s.grade])
        return output.getvalue()