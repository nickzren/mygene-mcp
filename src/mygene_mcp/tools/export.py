"""Data export tools."""

from typing import Any, Dict, List, Optional
import html
import json
import csv
import io
import re
from ..client import MyGeneClient

class ExportApi:
    """Tools for exporting gene data."""
    _XML_TAG_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")

    @staticmethod
    def _extract_field_value(gene: Dict[str, Any], field: str) -> Any:
        if "." not in field:
            return gene.get(field)

        value: Any = gene
        for part in field.split("."):
            if isinstance(value, dict):
                if part not in value:
                    return None
                value = value[part]
                continue

            if isinstance(value, list):
                next_values: List[Any] = []
                for item in value:
                    if isinstance(item, dict) and part in item:
                        next_values.append(item[part])
                if not next_values:
                    return None

                flattened: List[Any] = []
                for item in next_values:
                    if isinstance(item, list):
                        flattened.extend(item)
                    else:
                        flattened.append(item)
                value = flattened
                continue

            return None
        return value

    @classmethod
    def _validate_xml_fields(cls, fields: List[str]) -> None:
        invalid = []
        for field in fields:
            if not cls._XML_TAG_PATTERN.match(field):
                invalid.append(field)
                continue
            if field.lower().startswith("xml"):
                invalid.append(field)
        if invalid:
            invalid_fields = ", ".join(invalid)
            raise ValueError(f"Invalid XML field name(s): {invalid_fields}")

    async def export_gene_list(
        self,
        client: MyGeneClient,
        gene_ids: List[str],
        format: str = "tsv",
        fields: Optional[List[str]] = None
    ) -> str:
        """Export gene data in various formats."""
        # Default fields if not specified
        if not fields:
            fields = ["symbol", "name", "taxid", "entrezgene", "ensembl.gene", "type_of_gene"]
        
        # Fetch gene data
        fields_str = ",".join(fields)
        post_data = {
            "ids": gene_ids,
            "fields": fields_str
        }
        
        results = await client.post("gene", post_data)
        export_format = format
        
        # Format based on requested type
        if export_format == "json":
            return json.dumps(results, indent=2)
        
        elif export_format in ["tsv", "csv"]:
            # Flatten nested fields
            flattened_results = []
            for gene in results:
                flat_gene = {}
                for field in fields:
                    flat_gene[field] = self._extract_field_value(gene, field)
                
                flattened_results.append(flat_gene)
            
            # Create CSV/TSV
            output = io.StringIO()
            delimiter = "\t" if export_format == "tsv" else ","
            writer = csv.DictWriter(output, fieldnames=fields, delimiter=delimiter)
            
            writer.writeheader()
            writer.writerows(flattened_results)
            
            return output.getvalue()
        
        elif export_format == "xml":
            self._validate_xml_fields(fields)
            # Simple XML format
            xml_output = ['<?xml version="1.0" encoding="UTF-8"?>']
            xml_output.append("<genes>")
            
            for gene in results:
                xml_output.append("  <gene>")
                for field in fields:
                    value = self._extract_field_value(gene, field)
                    if value is None:
                        value_text = ""
                    elif isinstance(value, (list, dict)):
                        value_text = json.dumps(value)
                    else:
                        value_text = str(value)
                    escaped_value = html.escape(value_text, quote=True)
                    xml_output.append(f"    <{field}>{escaped_value}</{field}>")
                xml_output.append("  </gene>")
            
            xml_output.append("</genes>")
            return "\n".join(xml_output)
        
        else:
            raise ValueError(f"Unsupported format: {export_format}")
