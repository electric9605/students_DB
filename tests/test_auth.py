
def test_register_success(client, db_session):
    """егистрация с валидными данными"""
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "NewPass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "user_id" in data

def test_login_success(client, test_user):
    """Вход с правильными данными"""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "TestPass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == test_user.id

def test_login_wrong_password(client, test_user):
    """❌ Вход с неверным паролем"""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "WrongPass999"
    })
    assert response.status_code == 401
    assert "Неверное имя пользователя или пароль" in response.json()["detail"]

def test_register_invalid_password(client):
    """❌ Регистрация со слабым паролем"""
    response = client.post("/auth/register", json={
        "username": "baduser",
        "email": "bad@example.com",
        "password": "weak"
    })
    assert response.status_code == 422
    detail = str(response.json())
    assert "8 characters" in detail or "Пароль должен содержать" in detail