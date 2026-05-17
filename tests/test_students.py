from models import Student

def test_get_students_unauthorized(client):
    """Запрос к защищённому эндпоинту без заголовка"""
    response = client.get("/students/")
    assert response.status_code == 422
    assert "X-User-ID" in str(response.json())

def test_get_students_authorized(client, test_user):
    """Запрос с валидным X-User-ID возвращает список"""
    response = client.get("/students/", headers={"X-User-ID": str(test_user.id)})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_student_by_id_not_found(client, test_user):
    """Запрос несуществующего студента"""
    response = client.get("/students/99999", headers={"X-User-ID": str(test_user.id)})
    assert response.status_code == 404
    assert "Студент не найден" in response.json()["detail"]

def test_get_student_by_id_success(client, test_user, db_session):
    """Запрос существующего студента"""
    student = Student(
        last_name="Тестов",
        first_name="Тест",
        faculty="ФТФ",
        subject="Тестовый предмет",
        grade=100
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    
    response = client.get(f"/students/{student.id}", headers={"X-User-ID": str(test_user.id)})
    assert response.status_code == 200
    data = response.json()
    assert data["last_name"] == "Тестов"
    assert data["grade"] == 100