"""Genomic interval query tools."""

from typing import Any, Dict, Optional
from ..client import MyGeneClient

class IntervalApi:
    """Tool for querying genes by genomic interval."""
    
    async def query_genes_by_interval(
        self,
        client: MyGeneClient,
        chr: str,
        start: int,
        end: int,
        species: Optional[str] = "human",
        fields: Optional[str] = "symbol,name,taxid,entrezgene",
        size: Optional[int] = 10
    ) -> Dict[str, Any]:
        """Query genes by genomic interval (chromosome position)."""
        # Fix: Check if chr already has prefix
        if chr.startswith("chr"):
            q = f"{chr}:{start}-{end}"
        else:
            q = f"chr{chr}:{start}-{end}"
        
        params = {
            "q": q,
            "species": species,
            "fields": fields,
            "size": size
        }
        
        result = await client.get("query", params=params)
        
        return {
            "success": True,
            "interval": {
                "chr": chr,
                "start": start,
                "end": end,
                "species": species
            },
            "total": result.get("total", 0),
            "hits": result.get("hits", [])
        }

