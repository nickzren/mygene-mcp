"""Tests for MyGene HTTP client lifecycle behavior."""

import asyncio

import httpx
import pytest

from mygene_mcp.client import MyGeneClient, MyGeneError


@pytest.mark.asyncio
async def test_client_use_after_close_raises():
    client = MyGeneClient(base_url="https://example.org")
    await client.close()

    with pytest.raises(MyGeneError, match="Client is closed"):
        await client.get("query")

    with pytest.raises(MyGeneError, match="Client is closed"):
        await client.post("query", {"q": "CDK2"})


@pytest.mark.asyncio
async def test_client_double_close_is_safe():
    client = MyGeneClient(base_url="https://example.org")
    await client.close()
    await client.close()


@pytest.mark.asyncio
async def test_client_async_context_manager_closes_client():
    async with MyGeneClient(base_url="https://example.org") as client:
        assert client._closed is False

    assert client._closed is True

    with pytest.raises(MyGeneError, match="Client is closed"):
        await client.get("query")


@pytest.mark.asyncio
async def test_client_supports_concurrent_requests():
    counter = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        counter["count"] += 1
        return httpx.Response(
            200,
            json={"endpoint": request.url.path},
            request=request,
        )

    client = MyGeneClient(base_url="https://example.org")
    await client._client.aclose()
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=client.timeout)

    responses = await asyncio.gather(
        client.get("query/1"),
        client.get("query/2"),
        client.get("query/3"),
    )

    assert counter["count"] == 3
    assert [response["endpoint"] for response in responses] == ["/query/1", "/query/2", "/query/3"]

    await client.close()
