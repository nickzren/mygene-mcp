"""Metadata and utility tools."""

from typing import Any, Dict
from ..client import MyGeneClient

class MetadataApi:
    """Tools for retrieving MyGene.info metadata."""
    
    async def get_mygene_metadata(self, client: MyGeneClient) -> Dict[str, Any]:
        """Get metadata about the MyGene.info API service."""
        result = await client.get("metadata")
        
        return {
            "success": True,
            "metadata": result
        }
    
    async def get_available_fields(self, client: MyGeneClient) -> Dict[str, Any]:
        """Get a list of all available fields in MyGene.info."""
        result = await client.get("metadata/fields")
        
        return {
            "success": True,
            "fields": result
        }
    
    async def get_species_list(self, client: MyGeneClient) -> Dict[str, Any]:
        """Get a list of all supported species in MyGene.info."""
        # Query for species facets
        params = {
            "q": "*",
            "facets": "taxid",
            "facet_size": 1000,
            "size": 0
        }
        
        result = await client.get("query", params=params)
        
        # Process facets to create species list
        species_list = []
        if "facets" in result and "taxid" in result["facets"]:
            terms = result["facets"]["taxid"]["terms"]
            
            # Common species mapping
            common_names = {
                9606: "human",
                10090: "mouse",
                10116: "rat",
                7227: "fruitfly",
                6239: "nematode",
                7955: "zebrafish",
                3702: "thale-cress",
                8364: "frog",
                9823: "pig"
            }
            
            for term in terms:
                taxid = term["term"]
                count = term["count"]
                name = common_names.get(taxid, f"taxid:{taxid}")
                species_list.append({
                    "taxid": taxid,
                    "name": name,
                    "gene_count": count
                })
        
        return {
            "success": True,
            "total_species": len(species_list),
            "species": species_list
        }

