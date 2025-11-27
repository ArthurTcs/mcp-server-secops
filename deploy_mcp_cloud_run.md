# Deploying SecOps MCP Server to Cloud Run

This guide explains how to deploy the SecOps MCP server to Google Cloud Run and connect it to your SOC Agent.

## Prerequisites

- Google Cloud Project with Cloud Run API enabled
- `gcloud` CLI installed and authenticated
- Docker installed (optional, for local testing)

## 1. Build and Deploy to Cloud Run

Navigate to the `mcp-security/server/secops` directory:

```bash
cd mcp-security/server/secops
```

Submit the build to Cloud Build and deploy to Cloud Run:

```bash
# Set your project ID
export PROJECT_ID=your-project-id
export REGION=us-central1
export SERVICE_NAME=secops-mcp

# Submit build
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Deploy to Cloud Run
# Note: You need to pass the required environment variables
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars CHRONICLE_PROJECT_ID=your-chronicle-project-id \
  --set-env-vars CHRONICLE_CUSTOMER_ID=your-chronicle-customer-id \
  --set-env-vars CHRONICLE_REGION=us
```

> [!IMPORTANT]
> **Authentication**: The `--allow-unauthenticated` flag is used here for simplicity. For production, you should secure your service and configure authentication.
>
> **Service Account**: Ensure the Cloud Run service account has the necessary permissions to access Chronicle/SecOps API. You may need to mount the service account key or use Workload Identity.

## 2. Connect SOC Agent to Cloud Run

Once deployed, get the service URL:

```bash
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'
```

Update your `.env` file for the `soc_agent`:

```bash
# Add this line to your .env file
SECOPS_MCP_URL=https://your-service-url.a.run.app/sse
```

> [!NOTE]
> Ensure you append `/sse` to the URL if using SSE transport, or the appropriate endpoint for your configuration. The default `FastMCP` server exposes an SSE endpoint at `/sse`.

## 3. Verify Connection

Restart your SOC Agent. It should now connect to the remote MCP server instead of starting a local subprocess. Check the logs for:

```
Connecting to remote SecOps MCP server at https://...
```
