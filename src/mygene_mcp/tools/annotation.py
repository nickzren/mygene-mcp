"""Gene annotation tools."""

from typing import Any, Dict, Optional
from ..client import MyGeneClient

class AnnotationApi:
    """Tool for retrieving gene annotations from MyGene.info API."""
    
    async def get_gene_annotation(
        self,
        client: MyGeneClient,
        gene_id: str,
        fields: Optional[str] = None,
        species: Optional[str] = None,
        dotfield: Optional[bool] = True
    ) -> Dict[str, Any]:
        """Get detailed annotation for a specific gene by ID."""
        params = {}
        if fields:
            params["fields"] = fields
        if species:
            params["species"] = species
        if not dotfield:
            params["dotfield"] = "false"
        
        result = await client.get(f"gene/{gene_id}", params=params)
        
        return {
            "success": True,
            "gene": result
        }

