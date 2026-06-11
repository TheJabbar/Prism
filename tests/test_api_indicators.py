import pytest


@pytest.mark.asyncio
async def test_indicators_macro(client):
    response = await client.get("/api/v1/indicators/macro")
    assert response.status_code == 200
    data = response.json()
    assert "monetary_policy" in data
    assert "inflation" in data
    assert "growth" in data
    assert "external_sector" in data
    assert "banking" in data
    assert "fiscal" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_indicators_global(client):
    response = await client.get("/api/v1/indicators/global")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_indicators_content(client):
    response = await client.get("/api/v1/indicators/macro")
    data = response.json()
    mp = data["monetary_policy"]
    assert any(i["name"] == "BI-7DRR" for i in mp)
    assert any(i["name"] == "GDP Growth YoY" for i in data["growth"])
