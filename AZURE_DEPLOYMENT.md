# Azure Deployment Guide

This guide explains how to deploy the Prompt Quality Evaluator to Azure Container Apps.

## Prerequisites

1. An Azure account with an active subscription
2. Azure CLI installed locally (for manual setup)
3. GitHub repository with the code

## Azure Resources Required

The deployment uses the following Azure services:
- **Azure Container Registry (ACR)**: Stores Docker images
- **Azure Container Apps**: Hosts the application
- **Azure Container Apps Environment**: Manages the container app runtime

## Setup Instructions

### 1. Create Azure Resources

First, create the required Azure resources. You can do this via Azure Portal or Azure CLI.

#### Using Azure CLI

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="prompt-quality-evaluator-rg"
LOCATION="eastus"
CONTAINER_REGISTRY="promptqualityevaluator"
CONTAINER_APP_NAME="prompt-quality-evaluator"
CONTAINER_APP_ENV="prompt-quality-evaluator-env"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_REGISTRY \
  --sku Basic \
  --admin-enabled true

# Create Container Apps Environment
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### 2. Configure GitHub Secrets

Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions):

#### AZURE_CREDENTIALS

Create a service principal for GitHub Actions:

```bash
az ad sp create-for-rbac \
  --name "github-actions-prompt-quality-evaluator" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/prompt-quality-evaluator-rg \
  --sdk-auth
```

Copy the entire JSON output and add it as the `AZURE_CREDENTIALS` secret in GitHub.

#### Application Secrets

Add these secrets with your actual values:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_BASE_URL`: OpenRouter base URL
- `ANTHROPIC_LLM_MODEL`: Anthropic model identifier (e.g., `anthropic/opus-4.5`)
- `GOOGLE_LLM_MODEL`: Google model identifier
- `OPENAI_LLM_MODEL`: OpenAI model identifier

### 3. Deploy via GitHub Actions

The application automatically deploys when you push to the `master` branch.

```bash
git add .
git commit -m "Configure Azure deployment"
git push origin master
```

The GitHub Actions workflow will:
1. Build the Docker image
2. Push it to Azure Container Registry
3. Create or update the Container App
4. Display the application URL

### 4. Manual Deployment (Alternative)

If you prefer to deploy manually:

```bash
# Build and push Docker image
az acr build \
  --registry $CONTAINER_REGISTRY \
  --image $CONTAINER_APP_NAME:latest \
  --file infra/Dockerfile \
  .

# Create container app
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $CONTAINER_REGISTRY.azurecr.io/$CONTAINER_APP_NAME:latest \
  --target-port 8000 \
  --ingress external \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --registry-server $CONTAINER_REGISTRY.azurecr.io \
  --env-vars \
    OPENROUTER_API_KEY="your-api-key" \
    OPENROUTER_BASE_URL="your-base-url" \
    ANTHROPIC_LLM_MODEL="your-model" \
    GOOGLE_LLM_MODEL="your-model" \
    OPENAI_LLM_MODEL="your-model"
```

## Configuration

### Environment Variables

The application requires these environment variables:
- `OPENROUTER_API_KEY`: API key for OpenRouter
- `OPENROUTER_BASE_URL`: Base URL for OpenRouter API
- `ANTHROPIC_LLM_MODEL`: Model to use for Anthropic
- `GOOGLE_LLM_MODEL`: Model to use for Google
- `OPENAI_LLM_MODEL`: Model to use for OpenAI

### Scaling

Azure Container Apps automatically scales based on HTTP traffic:
- **Min replicas**: 0 (scales to zero when idle)
- **Max replicas**: 10
- **CPU**: 1.0 vCPU
- **Memory**: 2.0 GB

You can adjust these in the workflow file (`.github/workflows/deploy.yml`).

## Accessing the Application

After deployment, get your application URL:

```bash
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

The application will be available at: `https://<your-app-fqdn>`

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /evaluate` - Evaluate a prompt
- `POST /rewrite` - Rewrite a prompt
- `POST /grade` - Grade a prompt

## Monitoring

### View Logs

```bash
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow
```

### View Metrics

Use Azure Portal to view:
- Request metrics
- Response times
- Error rates
- Container resource usage

## Troubleshooting

### Check Container App Status

```bash
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.runningStatus
```

### View Recent Revisions

```bash
az containerapp revision list \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

### Common Issues

1. **Container fails to start**: Check environment variables are set correctly
2. **500 errors**: Review application logs for errors
3. **Authentication errors**: Verify API keys are valid

## Cost Management

Azure Container Apps pricing:
- Pay only for vCPU and memory consumed
- Free tier includes 180,000 vCPU-seconds and 360,000 GiB-seconds per month
- With min replicas set to 0, the app scales to zero when idle (no cost)

## Cleanup

To remove all Azure resources:

```bash
az group delete \
  --name $RESOURCE_GROUP \
  --yes --no-wait
```

## Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Container Registry Documentation](https://learn.microsoft.com/en-us/azure/container-registry/)
- [GitHub Actions for Azure](https://github.com/Azure/actions)
