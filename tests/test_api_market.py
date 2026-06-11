import pytest


@pytest.mark.asyncio
async def test_market_summary(client):
    response = await client.get("/api/v1/market/summary")
    assert response.status_code == 200
    data = response.json()
    assert "ihsg" in data
    assert "usdidr" in data
    assert "bi_rate" in data
    assert "sbn_10y" in data
    assert "dxy" in data
    assert "brent" in data
    assert "cpo" in data


@pytest.mark.asyncio
async def test_market_snapshots(client):
    response = await client.get("/api/v1/market/snapshots")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_market_indicators(client):
    response = await client.get("/api/v1/market/indicators")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_market_summary_structure(client):
    response = await client.get("/api/v1/market/summary")
    data = response.json()
    assert isinstance(data["ihsg"]["last"], (int, float))
    assert isinstance(data["ihsg"]["change_pct"], (int, float))
    assert isinstance(data["usdidr"]["last"], (int, float))
