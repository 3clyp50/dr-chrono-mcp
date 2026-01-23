"""DrChrono MCP Server - Main entry point.

This MCP server provides tools for interacting with the DrChrono healthcare API,
including patient management, appointments, clinical notes, billing, FHIR access,
and persistent clinical memory via SimpleMem.
"""

import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server

from drchrono_mcp.auth.oauth import OAuthManager
from drchrono_mcp.auth.token_store import TokenStore
from drchrono_mcp.clients.fhir_client import FHIRClient
from drchrono_mcp.clients.rest_client import DrChronoClient
from drchrono_mcp.clients.simplemem_client import SimpleMemClient
from drchrono_mcp.tools import (
    register_auth_tools,
    register_billing_tools,
    register_clinical_context_tools,
    register_clinical_tools,
    register_fhir_tools,
    register_lab_imaging_tools,
)

# Load environment variables
load_dotenv()


def get_env_or_error(name: str) -> str:
    """Get required environment variable or exit with helpful error."""
    value = os.getenv(name)
    if not value:
        print(f"Error: Required environment variable {name} is not set.", file=sys.stderr)
        print(f"Please set {name} in your environment or .env file.", file=sys.stderr)
        sys.exit(1)
    return value


@asynccontextmanager
async def create_server():
    """Create and configure the MCP server with all tools.

    Yields:
        Configured MCP Server instance
    """
    # Get OAuth credentials
    client_id = get_env_or_error("DRCHRONO_CLIENT_ID")
    client_secret = get_env_or_error("DRCHRONO_CLIENT_SECRET")
    redirect_uri = os.getenv("DRCHRONO_REDIRECT_URI", "http://localhost:8765/callback")

    # Optional token file location
    token_file = os.getenv("DRCHRONO_TOKEN_FILE")
    token_store = TokenStore(token_file) if token_file else TokenStore()

    # Initialize OAuth manager
    oauth = OAuthManager(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        token_store=token_store,
    )

    # Initialize REST client
    rest_client = DrChronoClient(oauth)

    # Initialize FHIR client (optional)
    fhir_base_url = os.getenv("DRCHRONO_FHIR_BASE_URL")
    fhir_client_id = os.getenv("DRCHRONO_FHIR_CLIENT_ID")
    fhir_client_secret = os.getenv("DRCHRONO_FHIR_CLIENT_SECRET")

    fhir_client = None
    if fhir_base_url:
        fhir_client = FHIRClient(
            base_url=fhir_base_url,
            client_id=fhir_client_id,
            client_secret=fhir_client_secret,
        )

    # Initialize SimpleMem client (optional - for persistent clinical memory)
    simplemem_url = os.getenv("SIMPLEMEM_API_URL")
    simplemem_token = os.getenv("SIMPLEMEM_ACCESS_TOKEN")

    memory_client = None
    if simplemem_url and simplemem_token:
        memory_client = SimpleMemClient(
            api_url=simplemem_url,
            access_token=simplemem_token,
        )

    # Create MCP server
    server = Server("drchrono-mcp")

    # Register all tools
    register_auth_tools(server, oauth)
    register_clinical_tools(server, rest_client)
    register_clinical_context_tools(server, rest_client, memory_client)
    register_billing_tools(server, rest_client)
    register_lab_imaging_tools(server, rest_client)
    register_fhir_tools(server, fhir_client)

    # Tools are automatically registered via @server.tool() decorators
    # in the register_*_tools functions above

    try:
        yield server
    finally:
        # Cleanup
        await rest_client.close()
        if fhir_client:
            await fhir_client.close()
        if memory_client:
            await memory_client.close()


async def run_server():
    """Run the MCP server."""
    async with create_server() as server:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )


def main():
    """Entry point for the MCP server."""
    import asyncio

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
