from fastapi.testclient import TestClient

from app.main import app


def test_demo_page_is_public_and_served_as_html():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.headers["cache-control"] == "no-store"
    assert 'id="ask-form"' in response.text
    assert 'type="password"' in response.text
    assert "localStorage" not in response.text


def test_demo_route_does_not_change_api_schema():
    assert "/" not in app.openapi()["paths"]
    assert "/ask" in app.openapi()["paths"]
