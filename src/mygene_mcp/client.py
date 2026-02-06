import httpx
from typing import Any, Dict, Optional


class MyGeneError(Exception):
    """Custom error for MyGene API operations."""
    pass


class MyGeneClient:
    """Client for MyGene.info API."""

    def __init__(self, base_url: str = "https://mygene.info/v3", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self._closed = False

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    async def __aenter__(self) -> "MyGeneClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to MyGene API."""
        if self._closed:
            raise MyGeneError("Client is closed.")

        try:
            response = await self._client.get(self._build_url(endpoint), params=params)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise MyGeneError("Request timed out. Please try again.")
        except httpx.HTTPStatusError as e:
            raise MyGeneError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except MyGeneError:
            raise
        except Exception as e:
            raise MyGeneError(f"Request failed: {str(e)}")

    async def close(self) -> None:
        """Close the shared HTTP client."""
        if self._closed:
            return
        await self._client.aclose()
        self._closed = True

    async def post(self, endpoint: str, json_data: Any) -> Any:
        """Make POST request to MyGene API."""
        if self._closed:
            raise MyGeneError("Client is closed.")

        try:
            response = await self._client.post(
                self._build_url(endpoint),
                json=json_data,
                headers={"content-type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise MyGeneError("Request timed out. Please try again.")
        except httpx.HTTPStatusError as e:
            raise MyGeneError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except MyGeneError:
            raise
        except Exception as e:
            raise MyGeneError(f"Request failed: {str(e)}")
