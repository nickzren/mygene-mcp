# MyGene MCP Server

[![CI](https://github.com/nickzren/mygene-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/nickzren/mygene-mcp/actions/workflows/ci.yml)
[![MCP Server](https://img.shields.io/badge/MCP-Server-0A66C2.svg)](https://modelcontextprotocol.io/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Model Context Protocol (MCP) server that exposes the [MyGene.info](https://mygene.info/) API as a set of tools for AI assistants.

## Features

### Core Capabilities

- **Gene Search**: Query genes by symbol, name, Entrez ID, Ensembl ID, or other identifiers
- **Gene Annotations**: Retrieve comprehensive gene information from multiple sources
- **Expression Queries**: Search genes by tissue expression or retrieve expression profiles
- **Pathway Queries**: Find genes in biological pathways or get pathway memberships
- **GO Annotations**: Search by GO terms or retrieve GO annotations with evidence codes
- **Disease Associations**: Find disease-associated genes or get gene-disease links
- **Drug/Chemical Interactions**: Search genes by drug/chemical or get interaction data
- **Ortholog/Homology**: Find orthologs across species or search homologous genes
- **Variant Information**: Retrieve genetic variants and clinical significance
- **Batch Operations**: Process up to 1000 genes in a single request
- **Genomic Interval Search**: Find genes by chromosomal coordinates
- **Advanced Queries**: Build complex queries with boolean logic and filters
- **Data Export**: Export gene lists in TSV, CSV, JSON, or XML formats

### Data Sources
- **NCBI**: Entrez Gene, RefSeq, HomoloGene
- **Ensembl**: Gene annotations, homology data
- **UniProt**: Protein annotations, GO terms
- **Human Protein Atlas (HPA)**: Tissue expression, subcellular localization
- **GTEx**: Gene expression in human tissues
- **BioGPS**: Gene expression profiles
- **ExAC**: Exome aggregation data
- **KEGG**: Pathways and disease associations
- **Reactome**: Biological pathways
- **WikiPathways**: Community pathways
- **BioCarta**: Pathway diagrams
- **NetPath**: Signal transduction pathways
- **PID**: Pathway Interaction Database
- **Gene Ontology**: Functional annotations
- **DisGeNET**: Disease-gene associations
- **ClinVar**: Clinical variants
- **OMIM**: Genetic disorders
- **PharmGKB**: Pharmacogenomics
- **DrugBank**: Drug targets
- **ChEMBL**: Bioactive compounds
- **ChEBI**: Chemical entities
- **InterPro**: Protein families and domains
- **Pfam**: Protein families
- **SMART**: Protein domains
- **PANTHER**: Gene function classification

## Prerequisites

- Python 3.12+ with pip

## Quick Start

### 1. Install UV
UV is a fast Python package and project manager.

```bash
pip install uv
```

### 2. Install MCPM (MCP Manager)
MCPM is a package manager for MCP servers that simplifies installation and configuration.

```bash
pip install mcpm
```

### 3. Setup the MCP Server
```bash
cd mygene-mcp
uv sync
```

### 4. Add the Server to Claude Desktop
```bash
# Make sure you're in the project directory
cd mygene-mcp

# Set Claude as the target client
mcpm target set @claude-desktop

# Add the MyGene MCP server
mcpm import stdio mygene \
  --command "$(uv run which python)" \
  --args "-m mygene_mcp.server"
```
Then restart Claude Desktop.

## Usage

#### Running the Server

```bash
uv run python -m mygene_mcp.server
```

You can choose a specific transport when starting the FastMCP server:

```bash
uv run python -m mygene_mcp.server --transport stdio        # default (Claude Desktop)
uv run python -m mygene_mcp.server --transport sse --host 0.0.0.0 --port 8000
uv run python -m mygene_mcp.server --transport http --host 0.0.0.0 --port 8000
```

When running with `--transport sse` or `--transport http`, the server exposes a discovery document at `/.well-known/mcp.json` and a health check at `/`.

#### Development

```bash
uv sync --extra dev
uv run pytest tests/ -v
```
