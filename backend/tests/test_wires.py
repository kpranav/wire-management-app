"""Tests for wire endpoints."""
import pytest
from httpx import AsyncClient

from app.models import Wire


@pytest.mark.asyncio
async def test_create_wire(client: AsyncClient, auth_headers: dict):
    """Test creating a wire."""
    response = await client.post(
        "/api/wires",
        json={
            "sender_name": "Alice Johnson",
            "recipient_name": "Bob Williams",
            "amount": 500.00,
            "currency": "USD",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sender_name"] == "Alice Johnson"
    assert data["recipient_name"] == "Bob Williams"
    assert float(data["amount"]) == 500.00
    assert data["currency"] == "USD"
    assert data["status"] == "pending"
    assert "reference_number" in data
    assert data["reference_number"].startswith("WIRE-")


@pytest.mark.asyncio
async def test_create_wire_unauthorized(client: AsyncClient):
    """Test creating a wire without auth fails."""
    response = await client.post(
        "/api/wires",
        json={
            "sender_name": "Alice Johnson",
            "recipient_name": "Bob Williams",
            "amount": 500.00,
            "currency": "USD",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_wires(client: AsyncClient, auth_headers: dict, test_wire: Wire):
    """Test listing wires."""
    response = await client.get("/api/wires", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "wires" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] >= 1
    assert len(data["wires"]) >= 1


@pytest.mark.asyncio
async def test_list_wires_pagination(client: AsyncClient, auth_headers: dict, test_wire: Wire):
    """Test wire list pagination."""
    response = await client.get(
        "/api/wires?page=1&page_size=10",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_wires_filter_by_status(
    client: AsyncClient, auth_headers: dict, test_wire: Wire
):
    """Test filtering wires by status."""
    response = await client.get(
        "/api/wires?status=pending",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert all(wire["status"] == "pending" for wire in data["wires"])


@pytest.mark.asyncio
async def test_get_wire(client: AsyncClient, auth_headers: dict, test_wire: Wire):
    """Test getting a specific wire."""
    response = await client.get(
        f"/api/wires/{test_wire.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_wire.id
    assert data["sender_name"] == test_wire.sender_name


@pytest.mark.asyncio
async def test_get_nonexistent_wire(client: AsyncClient, auth_headers: dict):
    """Test getting a nonexistent wire fails."""
    response = await client.get(
        "/api/wires/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_wire(client: AsyncClient, auth_headers: dict, test_wire: Wire):
    """Test updating a wire."""
    response = await client.put(
        f"/api/wires/{test_wire.id}",
        json={"amount": 2000.00, "status": "processing"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert float(data["amount"]) == 2000.00
    assert data["status"] == "processing"


@pytest.mark.asyncio
async def test_update_wire_invalid_status(
    client: AsyncClient, auth_headers: dict, test_wire: Wire
):
    """Test updating wire with invalid status fails."""
    response = await client.put(
        f"/api/wires/{test_wire.id}",
        json={"status": "invalid_status"},
        headers=auth_headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_wire(client: AsyncClient, auth_headers: dict, test_wire: Wire):
    """Test deleting a wire."""
    response = await client.delete(
        f"/api/wires/{test_wire.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(
        f"/api/wires/{test_wire.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_wire(client: AsyncClient, auth_headers: dict):
    """Test deleting a nonexistent wire fails."""
    response = await client.delete(
        "/api/wires/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404
