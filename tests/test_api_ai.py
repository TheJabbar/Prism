import pytest


@pytest.mark.asyncio
async def test_ai_chat(client):
    response = await client.post(
        "/api/v1/ai/chat",
        json={"message": "Apa kabar pasar Indonesia hari ini?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0


@pytest.mark.asyncio
async def test_ai_chat_with_history(client):
    response = await client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Apa yang terjadi dengan IHSG?",
            "history": [
                {"role": "assistant", "content": "Halo, ada yang bisa saya bantu?"},
                {"role": "user", "content": "Analisis pasar hari ini"},
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


@pytest.mark.asyncio
async def test_ai_insight(client):
    response = await client.post(
        "/api/v1/ai/insight",
        json={"include_headlines": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert "insight" in data
    assert "date" in data
