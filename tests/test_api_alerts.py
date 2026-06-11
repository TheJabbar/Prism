import pytest


@pytest.mark.asyncio
async def test_alerts_list(client):
    response = await client.get("/api/v1/alerts/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_alert_create(client):
    response = await client.post(
        "/api/v1/alerts/",
        json={
            "alert_type": "price",
            "symbol": "BBCA",
            "condition": "above",
            "threshold": 11000,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "price"
    assert "id" in data


@pytest.mark.asyncio
async def test_alert_create_and_delete(client):
    # Create
    create_resp = await client.post(
        "/api/v1/alerts/",
        json={
            "alert_type": "news_keyword",
            "keyword": "Bank Indonesia",
        },
    )
    alert_id = create_resp.json()["id"]

    # Delete
    delete_resp = await client.delete(f"/api/v1/alerts/{alert_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_alert_delete_not_found(client):
    response = await client.delete("/api/v1/alerts/99999")
    assert response.status_code == 404
