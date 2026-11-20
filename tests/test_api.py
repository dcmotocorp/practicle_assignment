from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path: Path):
    app = create_app(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def article_payload() -> dict[str, str]:
    return {
        "company_name": "Example Motors",
        "title": "Company announces investment in the new EV plan",
        "url": "https://example.com/news/ev-plan",
        "content": (
            "Example Motors announced a new electric vehicle plan. "
            "The company will spend 2 billion dollars on battery production. "
            "Construction will begin next year. The factory will create new jobs."
        ),
    }


def test_create_and_process_article(client: TestClient, article_payload: dict[str, str]) -> None:
    response = client.post("/articles", json=article_payload)
    assert response.status_code == 202
    created = response.json()
    assert created["status"] == "pending"
    assert created["category"] is None

    result = client.get(f"/articles/{created['id']}")
    assert result.status_code == 200
    processed = result.json()
    assert processed["status"] == "completed"
    assert processed["category"] == "automotive"
    assert processed["summary"]


def test_duplicate_url_returns_conflict(client: TestClient, article_payload: dict[str, str]) -> None:
    assert client.post("/articles", json=article_payload).status_code == 202
    response = client.post("/articles", json=article_payload)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "ARTICLE_URL_ALREADY_EXISTS"


def test_list_articles_with_filters_and_pagination(
    client: TestClient, article_payload: dict[str, str]
) -> None:
    client.post("/articles", json=article_payload)
    response = client.get(
        "/articles",
        params={"status": "completed", "category": "automotive", "page": 1, "page_size": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["pagination"] == {
        "page": 1, "page_size": 10, "total_items": 1, "total_pages": 1
    }


def test_validation_and_not_found_responses(client: TestClient) -> None:
    invalid = client.post(
        "/articles",
        json={"company_name": " ", "title": "News", "url": "not-a-url", "content": "Body"},
    )
    assert invalid.status_code == 422
    assert client.get("/articles/9999").status_code == 404


def test_swagger_and_openapi_are_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    assert "/articles" in schema.json()["paths"]
