"""Advanced query building tools."""

from typing import Any, Dict, Optional, List
from ..client import MyGeneClient

class AdvancedQueryApi:
    """Tools for building advanced queries."""
    
    async def build_complex_query(
        self,
        client: MyGeneClient,
        must: Optional[List[Dict]] = None,
        should: Optional[List[Dict]] = None,
        must_not: Optional[List[Dict]] = None,
        filters: Optional[Dict] = None,
        aggregations: Optional[Dict] = None,
        size: Optional[int] = 10
    ) -> Dict[str, Any]:
        """Build complex boolean queries with filters and aggregations."""
        # Build query parts
        query_parts = []
        
        # Handle MUST clauses (AND)
        if must:
            must_queries = []
            for clause in must:
                field = clause.get("field")
                value = clause.get("value")
                if field and value:
                    must_queries.append(f'{field}:"{value}"')
            
            if must_queries:
                query_parts.append(f'({" AND ".join(must_queries)})')
        
        # Handle SHOULD clauses (OR)
        if should:
            should_queries = []
            for clause in should:
                field = clause.get("field")
                value = clause.get("value")
                if field and value:
                    should_queries.append(f'{field}:"{value}"')
            
            if should_queries:
                query_parts.append(f'({" OR ".join(should_queries)})')
        
        # Handle MUST_NOT clauses (NOT)
        if must_not:
            for clause in must_not:
                field = clause.get("field")
                value = clause.get("value")
                if field and value:
                    query_parts.append(f'NOT {field}:"{value}"')
        
        # Apply filters
        if filters:
            for field, values in filters.items():
                if isinstance(values, list):
                    filter_query = " OR ".join([f'{field}:"{v}"' for v in values])
                    query_parts.append(f'({filter_query})')
                else:
                    query_parts.append(f'{field}:"{values}"')
        
        # Combine all parts
        if not query_parts:
            q = "*"
        else:
            q = " AND ".join(query_parts)
        
        # Prepare parameters
        params = {
            "q": q,
            "size": size
        }
        
        # Add aggregations if specified
        if aggregations:
            facet_fields: List[str] = []
            facet_size = 10
            for field, options in aggregations.items():
                if field == "size" and isinstance(options, int):
                    facet_size = options
                    continue
                if field == "fields" and isinstance(options, list):
                    facet_fields.extend(str(option) for option in options)
                    continue
                facet_fields.append(field)

            if facet_fields:
                params["facets"] = ",".join(facet_fields)
                params["facet_size"] = facet_size
        
        result = await client.get("query", params=params)
        
        response = {
            "success": True,
            "query": q,
            "total": result.get("total", 0),
            "hits": result.get("hits", [])
        }
        
        if aggregations and "facets" in result:
            response["aggregations"] = result["facets"]
        
        return response
    
    async def query_with_filters(
        self,
        client: MyGeneClient,
        q: str,
        type_of_gene: Optional[List[str]] = None,
        chromosome: Optional[List[str]] = None,
        taxid: Optional[List[int]] = None,
        ensembl_gene_exists: Optional[bool] = None,
        refseq_exists: Optional[bool] = None,
        has_go_annotation: Optional[bool] = None,
        has_pathway_annotation: Optional[bool] = None,
        size: Optional[int] = 10
    ) -> Dict[str, Any]:
        """Query with multiple filters applied."""
        # Start with base query
        query_parts = [q]
        
        # Apply type_of_gene filter
        if type_of_gene:
            type_query = " OR ".join([f'type_of_gene:"{t}"' for t in type_of_gene])
            query_parts.append(f'({type_query})')
        
        # Apply chromosome filter
        if chromosome:
            chr_query = " OR ".join([f'genomic_pos.chr:"{c}"' for c in chromosome])
            query_parts.append(f'({chr_query})')
        
        # Apply taxid filter
        if taxid:
            taxid_query = " OR ".join([f'taxid:{t}' for t in taxid])
            query_parts.append(f'({taxid_query})')
        
        # Apply existence filters
        if ensembl_gene_exists is not None:
            if ensembl_gene_exists:
                query_parts.append("_exists_:ensembl.gene")
            else:
                query_parts.append("NOT _exists_:ensembl.gene")
        
        if refseq_exists is not None:
            if refseq_exists:
                query_parts.append("_exists_:refseq")
            else:
                query_parts.append("NOT _exists_:refseq")
        
        if has_go_annotation is not None:
            if has_go_annotation:
                query_parts.append("_exists_:go")
            else:
                query_parts.append("NOT _exists_:go")
        
        if has_pathway_annotation is not None:
            if has_pathway_annotation:
                query_parts.append("_exists_:pathway")
            else:
                query_parts.append("NOT _exists_:pathway")
        
        # Combine query
        final_query = " AND ".join(query_parts)
        
        params = {
            "q": final_query,
            "size": size,
            "fields": "symbol,name,taxid,type_of_gene,genomic_pos,ensembl,refseq"
        }
        
        result = await client.get("query", params=params)
        
        return {
            "success": True,
            "query": final_query,
            "filters_applied": {
                "type_of_gene": type_of_gene,
                "chromosome": chromosome,
                "taxid": taxid,
                "ensembl_gene_exists": ensembl_gene_exists,
                "refseq_exists": refseq_exists,
                "has_go_annotation": has_go_annotation,
                "has_pathway_annotation": has_pathway_annotation
            },
            "total": result.get("total", 0),
            "hits": result.get("hits", [])
        }
