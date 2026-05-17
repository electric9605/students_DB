from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Student, User
import csv
import io
from typing import List, Tuple, Optional

class StudentCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Student:
        new_student = Student(**data)
        self.db.add(new_student)
        self.db.commit()
        self.db.refresh(new_student)
        return new_student

    def get_by_id(self, student_id: int) -> Optional[Student]:
        return self.db.query(Student).filter(Student.id == student_id).first()

    def get_all(self) -> List[Student]:
        return self.db.query(Student).all()

    def update(self, student_id: int, update_data: dict) -> Optional[Student]:
        student = self.get_by_id(student_id)
        if not student:
            return None
        for key, value in update_data.items():
            setattr(student, key, value)
        self.db.commit()
        self.db.refresh(student)
        return student

    def delete(self, student_id: int) -> bool:
        student = self.get_by_id(student_id)
        if not student:
            return False
        self.db.delete(student)
        self.db.commit()
        return True

    def get_by_faculty(self, faculty: str) -> List[Student]:
        return self.db.query(Student).filter(Student.faculty == faculty).all()

    def get_unique_courses(self) -> List[str]:
        return [row[0] for row in self.db.query(Student.subject).distinct().all()]

    def get_low_grades(self, course: str, threshold: int = 30) -> List[Student]:
        return self.db.query(Student).filter(
            Student.subject == course,
            Student.grade < threshold
        ).all()

    def get_avg_grade_by_faculty(self) -> List[Tuple[str, float]]:
        return self.db.query(
            Student.faculty,
            func.avg(Student.grade).label("avg_grade")
        ).group_by(Student.faculty).all()

    def export_to_csv(self) -> str:
        students = self.get_all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Фамилия", "Имя", "Факультет", "Курс", "Оценка"])
        for s in students:
            writer.writerow([s.last_name, s.first_name, s.faculty, s.subject, s.grade])
        return output.getvalue()
    
    def register_user(self, username: str, email: str, password: str) -> User:
        from auth import hash_password
        existing = self.db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing:
            raise ValueError("Пользователь с таким именем или email уже существует")
        
        new_user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_active=True
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        from auth import verify_password
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user