import pytest


@pytest.mark.asyncio
async def test_bonds_yield_curve(client):
    response = await client.get("/api/v1/bonds/yield-curve")
    assert response.status_code == 200
    data = response.json()
    assert "tenors" in data
    assert "yields" in data
    assert len(data["tenors"]) == len(data["yields"])


@pytest.mark.asyncio
async def test_bonds_benchmarks(client):
    response = await client.get("/api/v1/bonds/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert "bonds" in data
    assert len(data["bonds"]) > 0
    assert "isin" in data["bonds"][0]


@pytest.mark.asyncio
async def test_bonds_cds(client):
    response = await client.get("/api/v1/bonds/cds")
    assert response.status_code == 200
    data = response.json()
    assert "indonesia_5y" in data
    assert isinstance(data["indonesia_5y"], (int, float))


@pytest.mark.asyncio
async def test_bonds_auctions(client):
    response = await client.get("/api/v1/bonds/auctions")
    assert response.status_code == 200
    data = response.json()
    assert "upcoming" in data
    assert "historical" in data
