# tests/test_analytics.py
def test_avg_grades_unauthorized(client):
    """Аналитика без авторизации"""
    response = client.get("/analytics/avg-grades-by-faculty")
    assert response.status_code == 422  # Missing header

def test_avg_grades_authorized_empty(client, test_user):
    """Аналитика с авторизацией, но пустая БД - пустой список"""
    response = client.get("/analytics/avg-grades-by-faculty", headers={"X-User-ID": str(test_user.id)})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Пустая БД → пустой список, это корректно