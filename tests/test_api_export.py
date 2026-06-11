import pytest


@pytest.mark.asyncio
async def test_export_csv(client):
    response = await client.get("/api/v1/export/csv?module=market")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert "attachment" in response.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_export_json(client):
    response = await client.get("/api/v1/export/json?module=market")
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    assert "attachment" in response.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_export_csv_indicators(client):
    response = await client.get("/api/v1/export/csv?module=indicators")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_csv_portfolio(client):
    response = await client.get("/api/v1/export/csv?module=portfolio")
    assert response.status_code == 200
