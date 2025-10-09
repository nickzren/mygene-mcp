# src/mygene_mcp/client.py
import httpx
from typing import Any, Dict, Optional


class MyGeneError(Exception):
    """Custom error for MyGene API operations."""
    pass


class MyGeneClient:
    """Client for MyGene.info API."""
    
    def __init__(self, base_url: str = "https://mygene.info/v3", timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request to MyGene API."""
        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise MyGeneError("Request timed out. Please try again.")
            except httpx.HTTPStatusError as e:
                raise MyGeneError(f"HTTP error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                raise MyGeneError(f"Request failed: {str(e)}")

    async def close(self) -> None:
        """Close any persistent resources (placeholder for future enhancements)."""
        return None
    
    async def post(self, endpoint: str, json_data: Any) -> Any:
        """Make POST request to MyGene API."""
        url = f"{self.base_url}/{endpoint}"
        headers = {"content-type": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, json=json_data, headers=headers, timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise MyGeneError("Request timed out. Please try again.")
            except httpx.HTTPStatusError as e:
                raise MyGeneError(f"HTTP error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                raise MyGeneError(f"Request failed: {str(e)}")
