from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi import APIRouter
from sqlalchemy.orm import Session
from tasks import load_csv_task, delete_students_task
from cache import cached_response, cache_delete
from database import SessionLocal, engine, get_db
from models import Base, Student, User
from crud import StudentCRUD
from auth import get_current_user_by_id
from schemas import UserRegister, UserLogin, AuthResponse
import csv
import io
import asyncio

#  таблицы при старте
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student DB API", description="CRUD + аналитика по студентам")

#  зависимости

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_crud(db: Session = Depends(get_db)):
    return StudentCRUD(db)

# круд

@app.post("/students/", status_code=201)
def create_student(
    data: dict,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    return crud.create(data)

@app.get("/students/")
def get_students(
    skip: int = 0, limit: int = 100,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    return crud.get_all()[skip:skip+limit]

@app.get("/students/{student_id}")
def get_student(
    student_id: int,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    student = crud.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student

@app.put("/students/{student_id}")
def update_student(
    student_id: int, data: dict,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    updated = crud.update(student_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return updated

@app.delete("/students/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    if not crud.delete(student_id):
        raise HTTPException(status_code=404, detail="Студент не найден")

# аналитикс

@app.get("/analytics/faculty/{faculty}")
def get_students_by_faculty(
    faculty: str,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    return crud.get_by_faculty(faculty)

@app.get("/analytics/courses")
def get_unique_courses(
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    return crud.get_unique_courses()

@app.get("/analytics/low-grades/{course}")
def get_low_grade_students(
    course: str,
    threshold: int = Query(30, ge=0, le=100),
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    return crud.get_low_grades(course, threshold)

@app.get("/analytics/avg-grades-by-faculty")
def get_avg_grades(
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    results = crud.get_avg_grade_by_faculty()
    return [{"faculty": f, "avg_grade": round(avg, 2)} for f, avg in results]

@app.get("/export/csv")
def export_to_csv(
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    csv_data = crud.export_to_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"}
    )

# публичная авторизация

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    crud = StudentCRUD(db)
    try:
        user = crud.register_user(data.username, data.email, data.password)
        return AuthResponse(user_id=user.id, username=user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/login", response_model=AuthResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    crud = StudentCRUD(db)
    user = crud.authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    return AuthResponse(user_id=user.id, username=user.username)

app.include_router(auth_router)

@app.post("/admin/load-csv", status_code=202)
def trigger_csv_load(csv_path: str, current_user: User = Depends(get_current_user_by_id)):
    """Запускает фоновую загрузку CSV в БД"""
    # Проверка: только админ может загружать данные
    task = load_csv_task.delay(csv_path)
    return {
        "task_id": task.id,
        "message": "Загрузка запущена в фоне",
        "status_url": f"/admin/task/{task.id}"
    }

@app.post("/admin/delete-students", status_code=202)
def trigger_delete_students(
    student_ids: list[int],
    current_user: User = Depends(get_current_user_by_id)
):
    """Запускает фоновое удаление студентов по списку ID"""
    task = delete_students_task.delay(student_ids)
    # Инвалидируем кэш списка студентов
    cache_delete("students:*")
    return {
        "task_id": task.id,
        "message": "Удаление запущено в фоне",
        "status_url": f"/admin/task/{task.id}"
    }

@app.get("/students/")
@cached_response("students", expire=timedelta(minutes=5))
def get_students(
    skip: int = 0, limit: int = 100,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    return crud.get_all()[skip:skip+limit]

@app.get("/analytics/")
@cached_response("analytics", expire=timedelta(minutes=5))
def get_students(
    skip: int = 0, limit: int = 100,
    crud: StudentCRUD = Depends(get_crud),
    current_user: User = Depends(get_current_user_by_id)
):
    return crud.get_all()[skip:skip+limit]