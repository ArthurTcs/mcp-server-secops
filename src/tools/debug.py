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
"""Debug tools for SecOps MCP."""

import logging
from typing import Optional

from secops_mcp.server import get_chronicle_client, server

# Configure logging
logger = logging.getLogger('secops-mcp')

@server.tool()
async def verify_chronicle_connection(
    project_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    region: Optional[str] = None,
) -> str:
    """Verify connectivity to the Chronicle SIEM API.
    
    This tool attempts to initialize the Chronicle client and perform a lightweight
    API call (listing a single alert) to verify that authentication and network
    connectivity are working correctly.

    Args:
        project_id (Optional[str]): Google Cloud project ID. Defaults to environment configuration.
        customer_id (Optional[str]): Chronicle customer ID. Defaults to environment configuration.
        region (Optional[str]): Chronicle region (e.g., "us", "europe"). Defaults to environment configuration.

    Returns:
        str: A message indicating success or failure, including error details if applicable.
    """
    try:
        logger.info("Verifying Chronicle connection...")
        chronicle = get_chronicle_client(project_id, customer_id, region)
        
        # Try to fetch a single alert to verify access
        # We use a very short time window to minimize load, or just check if the call succeeds
        from datetime import datetime, timedelta, timezone
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=1)
        
        # We don't care about the result, just that the call doesn't raise an exception
        chronicle.get_alerts(
            start_time=start_time,
            end_time=end_time,
            max_alerts=1
        )
        
        return "✅ Connection to Chronicle SIEM verified successfully! Authentication and API access are working."
        
    except Exception as e:
        error_msg = f"❌ Connection failed: {str(e)}"
        logger.error(error_msg)
        return error_msg
