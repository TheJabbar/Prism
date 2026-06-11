"""
UI Functional Tests for PRISM Terminal.

These tests verify that the web UI responds correctly by checking
HTML structure, CSS loading, and JS module availability.
"""

import pytest


@pytest.mark.asyncio
async def test_ui_index_page(client):
    """Test that the main page loads with correct structure."""
    response = await client.get("/")
    assert response.status_code == 200
    html = response.text

    # Core structural elements
    assert "PRISM" in html
    assert "Indonesian Financial Intelligence Terminal" in html
    assert "sidebar" in html
    assert "mainContent" in html
    assert "tickerTape" in html


@pytest.mark.asyncio
async def test_ui_css_loaded(client):
    """Test that the CSS file is accessible."""
    response = await client.get("/static/css/prism.css")
    assert response.status_code == 200
    assert "text/css" in response.headers.get("content-type", "")
    assert "--bg-primary" in response.text
    assert "PRISM" in response.text


@pytest.mark.asyncio
async def test_ui_js_loaded(client):
    """Test that the JS file is accessible."""
    response = await client.get("/static/js/app.js")
    assert response.status_code == 200
    assert "application/javascript" in response.headers.get("content-type", "") or "text/javascript" in response.headers.get("content-type", "")
    assert "API_BASE" in response.text
    assert "loadDashboard" in response.text


@pytest.mark.asyncio
async def test_ui_all_modules_present(client):
    """Test that all 10 modules are defined in the HTML."""
    response = await client.get("/")
    html = response.text

    modules = [
        "module-dashboard",
        "module-market",
        "module-news",
        "module-indicators",
        "module-bonds",
        "module-fx",
        "module-portfolio",
        "module-ai",
        "module-alerts",
        "module-about",
    ]
    for mod in modules:
        assert mod in html, f"Missing module: {mod}"


@pytest.mark.asyncio
async def test_ui_nav_items(client):
    """Test that all navigation items are present."""
    response = await client.get("/")
    html = response.text

    nav_items = [
        "Dashboard",
        "Markets",
        "News",
        "Indicators",
        "Bonds",
        "FX",
        "Portfolio",
        "AI Analyst",
        "Alerts",
        "About",
    ]
    for item in nav_items:
        assert item in html, f"Missing nav item: {item}"


@pytest.mark.asyncio
async def test_ui_api_endpoint_consistency(client):
    """Test that the frontend JS uses the correct API base path."""
    response = await client.get("/static/js/app.js")
    js = response.text
    assert "/api/v1" in js


@pytest.mark.asyncio
async def test_ui_chartjs_loaded(client):
    """Test that Chart.js CDN is referenced in the HTML."""
    response = await client.get("/")
    html = response.text
    assert "chart.js" in html.lower() or "Chart" in html


@pytest.mark.asyncio
async def test_ui_ticker_tape_exists(client):
    """Test the ticker tape element exists in the UI."""
    response = await client.get("/")
    assert 'id="tickerTape"' in response.text
    assert "IHSG" in response.text
    assert "USD/IDR" in response.text
