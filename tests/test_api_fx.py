import pytest


@pytest.mark.asyncio
async def test_fx_rates(client):
    response = await client.get("/api/v1/fx/rates")
    assert response.status_code == 200
    data = response.json()
    assert "pairs" in data
    assert len(data["pairs"]) > 0
    assert data["pairs"][0]["pair"] == "USD/IDR"


@pytest.mark.asyncio
async def test_fx_jisdor(client):
    response = await client.get("/api/v1/fx/jisdor")
    assert response.status_code == 200
    data = response.json()
    assert "rate" in data
    assert "previous_rate" in data
    assert "ma_200" in data


@pytest.mark.asyncio
async def test_fx_dxy(client):
    response = await client.get("/api/v1/fx/dxy")
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert "sma_50" in data
    assert "sma_200" in data
