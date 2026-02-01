# Azure Deployment Guide

## Overview

This guide covers deploying the AI-Powered Workplace Automation System to Microsoft Azure using Azure App Service and Azure Container Registry.

---

## Prerequisites

- Azure subscription
- Azure CLI installed (`az`)
- Docker installed
- Git repository access
- OpenAI API key
- Pinecone account

---

## Step 1: Azure Setup

### 1.1 Login to Azure

```bash
az login
az account set --subscription "Your Subscription Name"
```

### 1.2 Create Resource Group

```bash
az group create \
  --name ai-workplace-automation-rg \
  --location eastus
```

### 1.3 Create Azure Container Registry

```bash
az acr create \
  --resource-group ai-workplace-automation-rg \
  --name aiworkplaceacr \
  --sku Basic \
  --admin-enabled true
```

### 1.4 Get ACR Credentials

```bash
az acr credential show --name aiworkplaceacr
```

Save the username and password for later use.

---

## Step 2: Build and Push Docker Image

### 2.1 Login to ACR

```bash
az acr login --name aiworkplaceacr
```

### 2.2 Build Docker Image

```bash
docker build -t ai-workplace-automation:latest .
```

### 2.3 Tag Image

```bash
docker tag ai-workplace-automation:latest \
  aiworkplaceacr.azurecr.io/ai-workplace-automation:latest
```

### 2.4 Push to ACR

```bash
docker push aiworkplaceacr.azurecr.io/ai-workplace-automation:latest
```

---

## Step 3: Create Azure App Service

### 3.1 Create App Service Plan

```bash
az appservice plan create \
  --name ai-workplace-plan \
  --resource-group ai-workplace-automation-rg \
  --is-linux \
  --sku B2
```

### 3.2 Create Web App

```bash
az webapp create \
  --resource-group ai-workplace-automation-rg \
  --plan ai-workplace-plan \
  --name ai-workplace-automation \
  --deployment-container-image-name aiworkplaceacr.azurecr.io/ai-workplace-automation:latest
```

### 3.3 Configure Container Registry

```bash
az webapp config container set \
  --name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg \
  --docker-custom-image-name aiworkplaceacr.azurecr.io/ai-workplace-automation:latest \
  --docker-registry-server-url https://aiworkplaceacr.azurecr.io \
  --docker-registry-server-user <ACR_USERNAME> \
  --docker-registry-server-password <ACR_PASSWORD>
```

---

## Step 4: Configure Environment Variables

### 4.1 Set Application Settings

```bash
az webapp config appsettings set \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-automation \
  --settings \
    ENV=production \
    OPENAI_API_KEY="your-openai-key" \
    PINECONE_API_KEY="your-pinecone-key" \
    PINECONE_ENVIRONMENT="your-env" \
    PINECONE_INDEX_NAME="workplace-docs" \
    SECRET_KEY="your-secret-key-here" \
    LOG_LEVEL=INFO \
    WORKER_COUNT=4
```

### 4.2 Optional: Use Azure Key Vault

For production, store secrets in Azure Key Vault:

```bash
# Create Key Vault
az keyvault create \
  --name ai-workplace-kv \
  --resource-group ai-workplace-automation-rg \
  --location eastus

# Add secrets
az keyvault secret set \
  --vault-name ai-workplace-kv \
  --name openai-api-key \
  --value "your-openai-key"

# Enable managed identity
az webapp identity assign \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-automation

# Grant access
az keyvault set-policy \
  --name ai-workplace-kv \
  --object-id <MANAGED_IDENTITY_ID> \
  --secret-permissions get list
```

---

## Step 5: Configure Continuous Deployment

### 5.1 Enable Continuous Deployment

```bash
az webapp deployment container config \
  --enable-cd true \
  --name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg
```

### 5.2 Get Webhook URL

```bash
az webapp deployment container show-cd-url \
  --name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg
```

### 5.3 Configure ACR Webhook

```bash
az acr webhook create \
  --registry aiworkplaceacr \
  --name aiworkplacewebhook \
  --actions push \
  --uri <WEBHOOK_URL>
```

---

## Step 6: Setup Microsoft Teams Bot

### 6.1 Create Bot Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Create "Azure Bot" resource
3. Set messaging endpoint: `https://ai-workplace-automation.azurewebsites.net/api/messages`

### 6.2 Configure Bot Settings

```bash
az webapp config appsettings set \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-automation \
  --settings \
    MICROSOFT_APP_ID="your-app-id" \
    MICROSOFT_APP_PASSWORD="your-app-password" \
    MICROSOFT_APP_TENANT_ID="your-tenant-id"
```

### 6.3 Add Teams Channel

1. In Azure Bot resource, go to Channels
2. Click Microsoft Teams
3. Enable the channel
4. Save configuration

---

## Step 7: Configure Redis (Optional)

For session management and caching:

```bash
# Create Azure Cache for Redis
az redis create \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0

# Get connection string
az redis list-keys \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-redis

# Configure app
az webapp config appsettings set \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-automation \
  --settings \
    REDIS_HOST="ai-workplace-redis.redis.cache.windows.net" \
    REDIS_PORT=6380 \
    REDIS_PASSWORD="<PRIMARY_KEY>" \
    REDIS_SSL=true
```

---

## Step 8: Configure Scaling

### 8.1 Enable Autoscaling

```bash
az monitor autoscale create \
  --resource-group ai-workplace-automation-rg \
  --resource ai-workplace-automation \
  --resource-type Microsoft.Web/sites \
  --name autoscale-settings \
  --min-count 1 \
  --max-count 5 \
  --count 2
```

### 8.2 Add Scaling Rules

```bash
# Scale up on high CPU
az monitor autoscale rule create \
  --resource-group ai-workplace-automation-rg \
  --autoscale-name autoscale-settings \
  --condition "CpuPercentage > 70 avg 5m" \
  --scale out 1

# Scale down on low CPU
az monitor autoscale rule create \
  --resource-group ai-workplace-automation-rg \
  --autoscale-name autoscale-settings \
  --condition "CpuPercentage < 30 avg 5m" \
  --scale in 1
```

---

## Step 9: Monitoring and Logging

### 9.1 Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app ai-workplace-insights \
  --location eastus \
  --resource-group ai-workplace-automation-rg

# Get instrumentation key
az monitor app-insights component show \
  --app ai-workplace-insights \
  --resource-group ai-workplace-automation-rg \
  --query instrumentationKey -o tsv

# Configure app
az webapp config appsettings set \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-automation \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY="<INSTRUMENTATION_KEY>"
```

### 9.2 Enable Diagnostic Logging

```bash
az webapp log config \
  --name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg \
  --application-logging true \
  --detailed-error-messages true \
  --failed-request-tracing true \
  --web-server-logging filesystem
```

### 9.3 View Logs

```bash
# Stream logs
az webapp log tail \
  --name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg

# Download logs
az webapp log download \
  --name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg \
  --log-file logs.zip
```

---

## Step 10: Security Configuration

### 10.1 Enable HTTPS Only

```bash
az webapp update \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-automation \
  --https-only true
```

### 10.2 Configure Custom Domain (Optional)

```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg \
  --hostname www.yourdomain.com

# Enable SSL
az webapp config ssl bind \
  --name ai-workplace-automation \
  --resource-group ai-workplace-automation-rg \
  --certificate-thumbprint <THUMBPRINT> \
  --ssl-type SNI
```

### 10.3 Configure Firewall Rules

```bash
# Restrict access to specific IPs (optional)
az webapp config access-restriction add \
  --resource-group ai-workplace-automation-rg \
  --name ai-workplace-automation \
  --rule-name "Office IP" \
  --action Allow \
  --ip-address 203.0.113.0/24 \
  --priority 100
```

---

## Step 11: Verify Deployment

### 11.1 Check Health Endpoint

```bash
curl https://ai-workplace-automation.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 11.2 Test API

```bash
curl -X POST https://ai-workplace-automation.azurewebsites.net/api/search/answer \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "top_k": 5}'
```

---

## CI/CD with GitHub Actions

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to ACR
        uses: azure/docker-login@v1
        with:
          login-server: aiworkplaceacr.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}
      
      - name: Build and push
        run: |
          docker build -t aiworkplaceacr.azurecr.io/ai-workplace-automation:${{ github.sha }} .
          docker push aiworkplaceacr.azurecr.io/ai-workplace-automation:${{ github.sha }}
      
      - name: Deploy to Azure
        uses: azure/webapps-deploy@v2
        with:
          app-name: ai-workplace-automation
          images: aiworkplaceacr.azurecr.io/ai-workplace-automation:${{ github.sha }}
```

---

## Cost Optimization

### Recommended Configuration

**Small-Scale (< 100 users):**
- App Service: B2 ($73/month)
- Redis: Basic C0 ($16/month)
- Estimated total: ~$100-150/month

**Medium-Scale (100-1000 users):**
- App Service: P1V2 ($146/month)
- Redis: Standard C1 ($55/month)
- Estimated total: ~$200-300/month

**Best Practices:**
- Use autoscaling to reduce costs during low-traffic periods
- Monitor Application Insights for optimization opportunities
- Use Azure Cost Management alerts

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

---

## Next Steps

1. Configure monitoring alerts
2. Set up backup strategy
3. Configure disaster recovery
4. Implement custom domain and SSL
5. Configure Teams app manifest

For support, contact your Azure administrator or visit [Azure Support](https://azure.microsoft.com/support/).
