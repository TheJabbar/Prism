import pytest


@pytest.mark.asyncio
async def test_portfolio_demo(client):
    response = await client.get("/api/v1/portfolio/demo")
    assert response.status_code == 200
    data = response.json()
    assert "portfolio" in data
    assert "holdings" in data
    assert data["portfolio"]["name"] == "Demo Portfolio"


@pytest.mark.asyncio
async def test_portfolio_list(client):
    response = await client.get("/api/v1/portfolio/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_portfolio_create(client):
    response = await client.post("/api/v1/portfolio/", json={"name": "Test Portfolio"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Portfolio"
    assert "id" in data


@pytest.mark.asyncio
async def test_holdings_create(client):
    # First create a portfolio
    portfolio_resp = await client.post("/api/v1/portfolio/", json={"name": "Holding Test"})
    portfolio_id = portfolio_resp.json()["id"]

    response = await client.post(
        "/api/v1/portfolio/holdings",
        json={
            "portfolio_id": portfolio_id,
            "ticker": "BBCA",
            "quantity": 100,
            "avg_price": 9500,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "BBCA"
