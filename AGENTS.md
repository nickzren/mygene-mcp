# Agent Guide — mygene-mcp

Brief for AI coding agents (Claude Code, Codex) working in this repo or routing biomedical questions through it.

## What this server is
MCP server wrapping the [MyGene.info](https://mygene.info/) API. Aggregates gene-centric annotations from NCBI, Ensembl, UniProt, HPA, GTEx, KEGG, Reactome, GO, DisGeNET, ClinVar, OMIM, PharmGKB, DrugBank, ChEMBL, InterPro, Pfam, PANTHER, …

## Run locally (stdio)
```bash
uv sync
uv run python -m mygene_mcp.server               # stdio (default)
```

HTTP/SSE: append `--transport http --host 127.0.0.1 --port 8000`.

## Use this server for
- Gene lookup by symbol, name, Entrez/Ensembl/UniProt/RefSeq IDs
- Comprehensive gene annotations from many sources in one record
- Tissue expression (HPA, GTEx, BioGPS), pathways (KEGG, Reactome, WikiPathways)
- GO term annotations with evidence codes
- Orthologs / homologs across species; genomic interval queries
- Batch operations (up to 1000 genes per request)
- Boolean / faceted advanced queries; export to TSV/CSV/JSON/XML

Prefer over other servers when the question is **gene-centric annotation aggregation** rather than scored target–disease evidence (use opentargets-mcp for that).

## Triage hints
- Symbol → ID resolution is built into the gene query; no separate resolver call needed.
- Use batch queries before iterating gene-by-gene.
- For "genes in pathway X" or "genes expressed in tissue Y", prefer the dedicated tool over building a boolean query.

## Pitfalls
- MyGene returns large nested records; ask only for the fields you need (the API supports field projection).
- Some species' annotations are sparser; empty fields are common, not errors.
- Variant data here is pointer-level (rsIDs, ClinVar links); use mydisease-mcp or opentargets-mcp for variant biology.

## Source layout
- `src/mygene_mcp/server.py` — FastMCP entrypoint
- `src/mygene_mcp/client.py` — HTTP client to MyGene.info
- `src/mygene_mcp/tools/` — tool implementations

## Dev
```bash
uv sync --extra dev
uv run pytest tests/ -v
```

## When editing tools
1. Add HTTP call in `client.py` if a new endpoint is needed.
2. Wrap in a tool under `src/mygene_mcp/tools/`; expose via the registry.
3. Add a unit test mocking the HTTP response.
