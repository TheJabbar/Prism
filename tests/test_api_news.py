import pytest


@pytest.mark.asyncio
async def test_news_list(client):
    response = await client.get("/api/v1/news/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_news_breaking(client):
    response = await client.get("/api/v1/news/breaking")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_news_seed(client):
    response = await client.post("/api/v1/news/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_news_after_seed(client):
    # First seed
    await client.post("/api/v1/news/seed")
    # Then list
    response = await client.get("/api/v1/news/")
    data = response.json()
    assert len(data) > 0
    assert "title" in data[0]
    assert "source" in data[0]


@pytest.mark.asyncio
async def test_news_filter_by_source(client):
    await client.post("/api/v1/news/seed")
    response = await client.get("/api/v1/news/?source=Kontan")
    data = response.json()
    for article in data:
        assert article["source"] == "Kontan"


@pytest.mark.asyncio
async def test_news_filter_by_language(client):
    await client.post("/api/v1/news/seed")
    response = await client.get("/api/v1/news/?language=en")
    data = response.json()
    for article in data:
        assert article["language"] == "en"
