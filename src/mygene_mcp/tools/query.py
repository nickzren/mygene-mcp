"""Gene query tools."""

from typing import Any, Dict, Optional, List
from ..client import MyGeneClient

class QueryApi:
    """Tool for querying genes from MyGene.info API."""
    
    async def query_genes(
        self,
        client: MyGeneClient,
        q: str,
        fields: Optional[str] = "symbol,name,taxid,entrezgene",
        species: Optional[str] = None,
        size: Optional[int] = 10,
        from_: Optional[int] = None,
        sort: Optional[str] = None,
        facets: Optional[str] = None,
        facet_size: Optional[int] = 10,
        fetch_all: Optional[bool] = False,
        scroll_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for genes using the MyGene.info query API."""
        params = {"q": q}
        if fields:
            params["fields"] = fields
        if species:
            params["species"] = species
        if size is not None:
            params["size"] = size
        if from_ is not None:
            params["from"] = from_
        if sort:
            params["sort"] = sort
        if facets:
            params["facets"] = facets
            params["facet_size"] = facet_size
        if fetch_all:
            params["fetch_all"] = "true"
        if scroll_id:
            params["scroll_id"] = scroll_id
        
        result = await client.get("query", params=params)
        
        return {
            "success": True,
            "total": result.get("total", 0),
            "took": result.get("took", 0),
            "hits": result.get("hits", []),
            "scroll_id": result.get("_scroll_id"),
            "facets": result.get("facets", {})
        }
    
    async def search_by_field(
        self,
        client: MyGeneClient,
        field_queries: Dict[str, str],
        operator: str = "AND",
        fields: Optional[str] = "symbol,name,taxid,entrezgene",
        species: Optional[str] = None,
        size: Optional[int] = 10
    ) -> Dict[str, Any]:
        """Search by specific fields with boolean operators."""
        # Build query string
        query_parts = []
        for field, value in field_queries.items():
            # Handle special characters in values
            if " " in value and not (value.startswith('"') and value.endswith('"')):
                value = f'"{value}"'
            query_parts.append(f"{field}:{value}")
        
        q = f" {operator} ".join(query_parts)
        
        return await self.query_genes(
            client=client,
            q=q,
            fields=fields,
            species=species,
            size=size
        )
    
    async def get_field_statistics(
        self,
        client: MyGeneClient,
        field: str,
        size: int = 100,
        species: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics for a specific field."""
        params = {
            "q": "*",
            "facets": field,
            "facet_size": size,
            "size": 0
        }
        if species:
            params["species"] = species
        
        result = await client.get("query", params=params)
        
        facet_data = result.get("facets", {}).get(field, {})
        terms = facet_data.get("terms", [])
        
        return {
            "success": True,
            "field": field,
            "total_unique_values": facet_data.get("total", 0),
            "top_values": [
                {
                    "value": term["term"],
                    "count": term["count"],
                    "percentage": round(term["count"] / result.get("total", 1) * 100, 2)
                }
                for term in terms
            ],
            "total_genes": result.get("total", 0)
        }

