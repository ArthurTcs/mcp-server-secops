# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Google Security Operations MCP server.

This module implements the Security Operations MCP server to perform
security operations tasks using Chronicle, including natural language search.
"""

import logging
import os
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from secops import SecOpsClient

# Initialize FastMCP server with a descriptive name
FASTMCP_LOG_LEVEL=os.environ.get('FASTMCP_LOG_LEVEL',"ERROR") 
server = FastMCP('Google Security Operations MCP server', FASTMCP_LOG_LEVEL)

# Configure logging
LOG_LEVEL=os.environ.get('LOG_LEVEL',logging.INFO) 
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger('secops-mcp')

# Constants
USER_AGENT = 'secops-app/1.0'

# Default Chronicle configuration from environment variables
DEFAULT_PROJECT_ID = os.environ.get('CHRONICLE_PROJECT_ID', '725716774503')
DEFAULT_CUSTOMER_ID = os.environ.get(
    'CHRONICLE_CUSTOMER_ID', 'c3c6260c1c9340dcbbb802603bbf9636'
)
DEFAULT_REGION = os.environ.get('CHRONICLE_REGION', 'us')


def get_chronicle_client(
    project_id: Optional[str] = None, 
    customer_id: Optional[str] = None, 
    region: Optional[str] = None
) -> Any:
    """Initialize and return a Chronicle client.

    Args:
        project_id: Google Cloud project ID (defaults to CHRONICLE_PROJECT_ID env var)
        customer_id: Chronicle customer ID (defaults to CHRONICLE_CUSTOMER_ID env var)
        region: Chronicle region (defaults to CHRONICLE_REGION env var or "us")

    Returns:
        Any: Initialized Chronicle client
    """
    # Use provided values or defaults from environment variables
    project_id = project_id or DEFAULT_PROJECT_ID
    customer_id = customer_id or DEFAULT_CUSTOMER_ID
    region = region or DEFAULT_REGION

    if not project_id or not customer_id:
        raise ValueError(
            'Chronicle project_id and customer_id must be provided either '
            'as parameters or through environment variables '
            '(CHRONICLE_PROJECT_ID, CHRONICLE_CUSTOMER_ID)'
        )

    client = SecOpsClient()
    chronicle = client.chronicle(
        customer_id=customer_id, project_id=project_id, region=region
    )
    return chronicle


# Import all tools
from secops_mcp.tools import *


def main() -> None:
    """Run the MCP server for SecOps tools.

    This function initializes and starts the MCP server with all the defined
    tools.
    """
    # Initialize and run the server
    server.run(transport='stdio')


if __name__ == '__main__':
    main()

# Expose ASGI app for Cloud Run
# FastMCP instance itself is not an ASGI app, we need to extract/create it.
try:
    if hasattr(server, 'create_asgi_app') and callable(server.create_asgi_app):
        app = server.create_asgi_app()
    elif hasattr(server, 'sse_app') and callable(server.sse_app):
        app = server.sse_app()
    elif hasattr(server, 'sse_app'):
        app = server.sse_app
    elif hasattr(server, '_mcp_server') and hasattr(server._mcp_server, 'app'):
        app = server._mcp_server.app
    else:
        # Fallback: maybe it IS callable?
        app = server
except Exception as e:
    logging.error(f"Error creating ASGI app: {e}")
    # If we can't find the app, uvicorn will likely fail when importing 'app', 
    # but we want to allow the module to import successfully if just running main().
    app = None
