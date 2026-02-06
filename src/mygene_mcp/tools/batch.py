"""Batch operation tools."""

from typing import Any, Dict, List, Optional
from ..client import MyGeneClient, MyGeneError

MAX_BATCH_SIZE = 1000

class BatchApi:
    """Tools for batch operations on genes."""
    
    async def query_genes_batch(
        self,
        client: MyGeneClient,
        gene_ids: List[str],
        scopes: Optional[str] = "entrezgene,ensemblgene,symbol",
        fields: Optional[str] = "symbol,name,taxid,entrezgene",
        species: Optional[str] = None,
        dotfield: Optional[bool] = True,
        returnall: Optional[bool] = True
    ) -> Dict[str, Any]:
        """Query multiple genes in a single request."""
        if len(gene_ids) > MAX_BATCH_SIZE:
            raise MyGeneError(f"Batch size exceeds maximum of {MAX_BATCH_SIZE}")
        
        post_data = {
            "q": gene_ids,
            "scopes": scopes,
            "fields": fields
        }
        if species:
            post_data["species"] = species
        if dotfield is False:
            post_data["dotfield"] = False
        # Fix: Always include returnall when it's explicitly set
        if returnall is not None:
            post_data["returnall"] = returnall
        
        results = await client.post("query", post_data)
        
        # Process results
        found = []
        missing = []
        for result in results:
            is_missing = bool(result.get("notfound"))
            if "found" in result:
                is_missing = not bool(result.get("found"))

            if is_missing:
                missing.append(result.get("query", "Unknown"))
            else:
                found.append(result)
        
        return {
            "success": True,
            "total": len(results),
            "found": len(found),
            "missing": len(missing),
            "results": results,
            "missing_ids": missing
        }
    
    async def get_genes_batch(
        self,
        client: MyGeneClient,
        gene_ids: List[str],
        fields: Optional[str] = None,
        species: Optional[str] = None,
        dotfield: Optional[bool] = True,
        filter_: Optional[str] = None,
        email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get annotations for multiple genes in a single request."""
        if len(gene_ids) > MAX_BATCH_SIZE:
            raise MyGeneError(f"Batch size exceeds maximum of {MAX_BATCH_SIZE}")
        
        post_data = {"ids": gene_ids}
        if fields:
            post_data["fields"] = fields
        if species:
            post_data["species"] = species
        if dotfield is False:
            post_data["dotfield"] = False
        if filter_:
            post_data["filter"] = filter_
        if email:
            post_data["email"] = email
        
        results = await client.post("gene", post_data)
        
        return {
            "success": True,
            "total": len(results),
            "genes": results
        }
