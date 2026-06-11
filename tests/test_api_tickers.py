import pytest


@pytest.mark.asyncio
async def test_tickers_list_empty(client):
    response = await client.get("/api/v1/tickers/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_tickers_seed(client):
    response = await client.post("/api/v1/tickers/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["count"] > 0


@pytest.mark.asyncio
async def test_tickers_list_after_seed(client):
    await client.post("/api/v1/tickers/seed")
    response = await client.get("/api/v1/tickers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "symbol" in data[0]
    assert "last_price" in data[0]


@pytest.mark.asyncio
async def test_tickers_get_one(client):
    await client.post("/api/v1/tickers/seed")
    response = await client.get("/api/v1/tickers/IHSG")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "IHSG"
    assert isinstance(data["last_price"], (int, float))


@pytest.mark.asyncio
async def test_tickers_get_not_found(client):
    response = await client.get("/api/v1/tickers/NONEXISTENT")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tickers_create(client):
    response = await client.post(
        "/api/v1/tickers/",
        json={
            "symbol": "TEST",
            "snapshot_type": "equity",
            "last_price": 1000.0,
            "change": 10.0,
            "change_pct": 1.01,
            "volume": 1000000,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "TEST"
    assert data["status"] == "updated"


@pytest.mark.asyncio
async def test_tickers_update(client):
    await client.post(
        "/api/v1/tickers/",
        json={"symbol": "UPDATE", "snapshot_type": "index", "last_price": 5000.0},
    )
    response = await client.post(
        "/api/v1/tickers/",
        json={"symbol": "UPDATE", "snapshot_type": "index", "last_price": 5100.0, "change": 100.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["last_price"] == 5100.0


@pytest.mark.asyncio
async def test_tickers_delete(client):
    await client.post(
        "/api/v1/tickers/",
        json={"symbol": "TODELETE", "snapshot_type": "equity", "last_price": 500.0},
    )
    response = await client.delete("/api/v1/tickers/TODELETE")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"


@pytest.mark.asyncio
async def test_tickers_delete_not_found(client):
    response = await client.delete("/api/v1/tickers/DOESNOTEXIST")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tickers_refresh(client):
    await client.post("/api/v1/tickers/seed")
    response = await client.post("/api/v1/tickers/refresh")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "refreshed"
    assert data["count"] > 0
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_tickers_has_initial_symbols(client):
    await client.post("/api/v1/tickers/seed")
    response = await client.get("/api/v1/tickers/")
    data = response.json()
    symbols = [t["symbol"] for t in data]
    assert "IHSG" in symbols
    assert "USD/IDR" in symbols
    assert "BBCA" in symbols
