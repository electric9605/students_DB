# main.py
from sqlalchemy.orm import Session
from models import Student, engine
from sqlalchemy import func

with Session(engine) as session:
    # Сколько всего записей
    print(f"📚 Всего записей: {session.query(Student).count()}")
    
    # Сколько уникальных студентов
    unique_students = session.query(
        Student.last_name, 
        Student.first_name
    ).distinct().count()
    print(f"👥 Уникальных студентов: {unique_students}")
    
    # Топ-3 предмета по количеству оценок
    print("\n📊 Оценок по предметам:")
    subjects = session.query(
        Student.subject, 
        func.count(Student.id)
    ).group_by(Student.subject).all()
    for subj, count in sorted(subjects, key=lambda x: x[1], reverse=True)[:3]:
        print(f"  {subj}: {count} оценок")
    
    # Средняя оценка
    avg_grade = session.query(func.avg(Student.grade)).scalar()
    print(f"\n📈 Средняя оценка: {avg_grade:.2f}")