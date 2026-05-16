from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base
from crud import StudentCRUD
import csv
import io


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student DB API", description="CRUD + аналитика по студентам")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_crud(db: Session = Depends(get_db)):
    return StudentCRUD(db)


@app.post("/students/", status_code=201)
def create_student(data: dict, crud: StudentCRUD = Depends(get_crud)):
    """Создание нового студента (INSERT)"""
    return crud.create(data)

@app.get("/students/")
def get_students(skip: int = 0, limit: int = 100, crud: StudentCRUD = Depends(get_crud)):
    """Получение списка студентов (SELECT)"""
    return crud.get_all()[skip:skip+limit]

@app.get("/students/{student_id}")
def get_student(student_id: int, crud: StudentCRUD = Depends(get_crud)):
    """Получение студента по ID"""
    student = crud.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student

@app.put("/students/{student_id}")
def update_student(student_id: int, data: dict, crud: StudentCRUD = Depends(get_crud)):
    """Обновление данных студента (UPDATE)"""
    updated = crud.update(student_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return updated

@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, crud: StudentCRUD = Depends(get_crud)):
    """Удаление студента (DELETE)"""
    if not crud.delete(student_id):
        raise HTTPException(status_code=404, detail="Студент не найден")


@app.get("/analytics/faculty/{faculty}")
def get_students_by_faculty(faculty: str, crud: StudentCRUD = Depends(get_crud)):
    """Студенты конкретного факультета"""
    return crud.get_by_faculty(faculty)

@app.get("/analytics/courses")
def get_unique_courses(crud: StudentCRUD = Depends(get_crud)):
    """Список уникальных предметов"""
    return crud.get_unique_courses()

@app.get("/analytics/low-grades/{course}")
def get_low_grade_students(course: str, threshold: int = Query(30, ge=0, le=100), crud: StudentCRUD = Depends(get_crud)):
    """Студенты по предмету с оценкой ниже порога (по умолч. 30)"""
    return crud.get_low_grades(course, threshold)

@app.get("/analytics/avg-grades-by-faculty")
def get_avg_grades(crud: StudentCRUD = Depends(get_crud)):
    """Средний балл в разрезе факультетов"""
    results = crud.get_avg_grade_by_faculty()
    return [{"faculty": f, "avg_grade": round(avg, 2)} for f, avg in results]

@app.get("/export/csv")
def export_to_csv(crud: StudentCRUD = Depends(get_crud)):
    """Выгрузка всей БД в CSV-файл"""
    csv_data = crud.export_to_csv()
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_export.csv"}
    )