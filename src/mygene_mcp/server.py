"""FastMCP-backed server for MyGene MCP tools."""
from __future__ import annotations

import anyio
import functools
import inspect
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, Optional, Tuple

import mcp.types as mcp_types
from fastmcp import FastMCP
from mcp.server.lowlevel.server import NotificationOptions
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from . import __version__ as package_version
from .client import MyGeneClient
from .tools import (
    AdvancedQueryApi,
    AnnotationApi,
    BatchApi,
    ChemicalApi,
    DiseaseApi,
    ExportApi,
    ExpressionApi,
    GOApi,
    HomologyApi,
    IntervalApi,
    MetadataApi,
    PathwayApi,
    QueryApi,
    VariantApi,
)

__all__ = [
    "mcp",
    "get_client",
    "main",
]

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Client lifecycle management
# ---------------------------------------------------------------------------
_client: Optional[MyGeneClient] = None


def _load_client_config() -> Dict[str, Any]:
    """Load client configuration from environment variables."""
    return {
        "base_url": os.getenv("MYGENE_BASE_URL", "https://mygene.info/v3"),
        "timeout": float(os.getenv("MYGENE_TIMEOUT", "30.0")),
    }


def get_client() -> MyGeneClient:
    """Return the active MyGeneClient or raise if not initialised."""
    if _client is None:
        raise RuntimeError(
            "MyGeneClient not initialised. Tools must be called through the running MCP server."
        )
    return _client


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Initialise and clean up shared resources for FastMCP."""
    global _client

    config = _load_client_config()
    logger.info(
        "Starting MyGene MCP server base_url=%s timeout=%s",
        config["base_url"],
        config["timeout"],
    )

    _client = MyGeneClient(
        base_url=config["base_url"],
        timeout=config["timeout"],
    )

    try:
        yield
    finally:
        if _client is not None:
            await _client.close()
            _client = None
            logger.info("MyGene MCP server shut down cleanly")


# ---------------------------------------------------------------------------
# FastMCP initialisation
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="mygene-mcp",
    version=package_version,
    lifespan=lifespan,
)

_query_api = QueryApi()
_annotation_api = AnnotationApi()
_batch_api = BatchApi()
_interval_api = IntervalApi()
_metadata_api = MetadataApi()
_expression_api = ExpressionApi()
_pathway_api = PathwayApi()
_go_api = GOApi()
_homology_api = HomologyApi()
_disease_api = DiseaseApi()
_variant_api = VariantApi()
_chemical_api = ChemicalApi()
_advanced_api = AdvancedQueryApi()
_export_api = ExportApi()


def _make_tool_wrapper(method: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap an API coroutine so the shared client is injected automatically."""

    @functools.wraps(method)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        client = get_client()
        return await method(client, *args, **kwargs)

    signature = inspect.signature(method)
    params = list(signature.parameters.values())[1:]
    wrapper.__signature__ = signature.replace(parameters=params)  # type: ignore[attr-defined]
    return wrapper


def register_all_api_methods() -> None:
    """Register every coroutine defined on the API classes as FastMCP tools."""
    api_instances: Tuple[Any, ...] = (
        _query_api,
        _annotation_api,
        _batch_api,
        _interval_api,
        _metadata_api,
        _expression_api,
        _pathway_api,
        _go_api,
        _homology_api,
        _disease_api,
        _variant_api,
        _chemical_api,
        _advanced_api,
        _export_api,
    )

    for api in api_instances:
        for name in dir(api):
            if name.startswith("_"):
                continue
            method = getattr(api, name)
            if not inspect.iscoroutinefunction(method):
                continue
            if name in getattr(mcp._tool_manager, "_tools", {}):
                logger.debug("Tool already registered: %s", name)
                continue
            wrapper = _make_tool_wrapper(method)
            mcp.tool(name=name)(wrapper)
            logger.debug("Registered tool: %s", name)


register_all_api_methods()


# ---------------------------------------------------------------------------
# Deprecated module-level guidance
# ---------------------------------------------------------------------------

def __getattr__(name: str) -> Any:  # pragma: no cover - guidance only
    if name == "ALL_TOOLS":
        raise AttributeError(
            "ALL_TOOLS has been removed in v0.3.0. Use FastMCP list_tools instead."
        )
    if name == "API_CLASS_MAP":
        raise AttributeError(
            "API_CLASS_MAP has been removed in v0.3.0. Tool dispatch is handled by FastMCP."
        )
    raise AttributeError(name)


# ---------------------------------------------------------------------------
# Discovery endpoints for HTTP/SSE transports
# ---------------------------------------------------------------------------


@mcp.custom_route("/.well-known/mcp.json", methods=["GET"], include_in_schema=False)
async def discovery_endpoint(request: Request) -> JSONResponse:
    """Expose MCP discovery metadata for HTTP/SSE clients."""

    base_url = str(request.base_url).rstrip("/")
    sse_path = mcp._deprecated_settings.sse_path.lstrip("/")
    message_path = mcp._deprecated_settings.message_path.lstrip("/")
    http_path = mcp._deprecated_settings.streamable_http_path.lstrip("/")

    capabilities = mcp._mcp_server.get_capabilities(
        NotificationOptions(),
        experimental_capabilities={}
    )

    transports: Dict[str, Dict[str, str]] = {
        "sse": {
            "url": f"{base_url}/{sse_path}",
            "messageUrl": f"{base_url}/{message_path}",
        }
    }

    transports["http"] = {
        "url": f"{base_url}/{http_path}",
    }

    discovery = {
        "protocolVersion": mcp_types.LATEST_PROTOCOL_VERSION,
        "server": {
            "name": mcp._mcp_server.name,
            "version": mcp._mcp_server.version,
            "instructions": mcp._mcp_server.instructions,
        },
        "capabilities": capabilities.model_dump(mode="json"),
        "transports": transports,
    }

    return JSONResponse(discovery)


@mcp.custom_route("/", methods=["GET"], include_in_schema=False)
async def root_health(_: Request) -> JSONResponse:
    """Simple health check endpoint."""

    return JSONResponse({"status": "ok"})


@mcp.custom_route(mcp._deprecated_settings.sse_path, methods=["POST"], include_in_schema=False)
async def sse_message_fallback(_: Request) -> Response:
    """Gracefully handle clients that POST to the SSE endpoint."""

    return Response(status_code=204)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="MyGene MCP Server",
        epilog="Environment overrides: MCP_TRANSPORT, FASTMCP_SERVER_HOST, FASTMCP_SERVER_PORT",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="Transport protocol to expose (stdio, sse, or http)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("FASTMCP_SERVER_HOST", "0.0.0.0"),
        help="Host for SSE transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("FASTMCP_SERVER_PORT", "8000")),
        help="Port for SSE transport (default: 8000)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG level) logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.transport in {"sse", "http"}:
        os.environ["FASTMCP_SERVER_HOST"] = args.host
        os.environ["FASTMCP_SERVER_PORT"] = str(args.port)
        if hasattr(mcp, "settings"):
            mcp.settings.host = args.host  # type: ignore[attr-defined]
            mcp.settings.port = args.port  # type: ignore[attr-defined]
        logger.info("Configured %s host=%s port=%s", args.transport.upper(), args.host, args.port)

    logger.info(
        "Starting MyGene MCP server (transport=%s, host=%s, port=%s)",
        args.transport,
        args.host,
        args.port,
    )

    try:
        if args.transport == "http":
            async def run_http() -> None:
                await mcp.run_http_async(host=args.host, port=args.port)

            anyio.run(run_http)
        else:
            mcp.run(transport=args.transport)
    except KeyboardInterrupt:  # pragma: no cover - user interaction
        logger.info("Server interrupted by user")
    except Exception:  # pragma: no cover - unexpected runtime failure
        logger.exception("Server encountered an unrecoverable error")
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
