# Troubleshooting Guide

## Common Issues and Solutions

This guide covers common issues you might encounter when using or deploying the AI-Powered Workplace Automation System.

---

## Installation & Setup Issues

### Issue: OpenAI API Key Not Working

**Symptoms:**
- Error: "Invalid API key"
- Authentication failures
- 401 Unauthorized errors

**Solutions:**

1. **Verify API Key:**
   ```bash
   # Check if key is set
   echo $OPENAI_API_KEY
   ```

2. **Check Key Format:**
   - Should start with `sk-`
   - No extra spaces or quotes
   - Not expired

3. **Test API Key:**
   ```python
   import openai
   openai.api_key = "your-key"
   openai.models.list()  # Should not raise error
   ```

4. **Regenerate Key:**
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create new key
   - Update `.env` file

---

### Issue: Pinecone Connection Failed

**Symptoms:**
- "Failed to connect to Pinecone"
- Index not found errors
- Timeout errors

**Solutions:**

1. **Check Credentials:**
   ```bash
   echo $PINECONE_API_KEY
   echo $PINECONE_ENVIRONMENT
   ```

2. **Verify Index Exists:**
   ```python
   from pinecone import Pinecone
   pc = Pinecone(api_key="your-key")
   print(pc.list_indexes())
   ```

3. **Create Index if Missing:**
   ```python
   from app.core.pinecone_service import create_pinecone_service
   
   service = create_pinecone_service()
   service.create_index()
   ```

4. **Check Region:**
   - Ensure `PINECONE_REGION` matches your index region
   - Update in `.env` if incorrect

---

### Issue: Docker Build Fails

**Symptoms:**
- Build errors during `docker build`
- Dependency installation failures
- Out of memory errors

**Solutions:**

1. **Increase Docker Memory:**
   - Docker Desktop → Settings → Resources
   - Increase memory to at least 4GB

2. **Clean Docker Cache:**
   ```bash
   docker system prune -a
   docker build --no-cache -t ai-workplace-automation .
   ```

3. **Check Dockerfile:**
   - Ensure all COPY paths are correct
   - Verify requirements.txt exists

4. **Build in Stages:**
   ```bash
   # Build only stage 1
   docker build --target builder -t builder .
   ```

---

## Runtime Issues

### Issue: Slow Response Times

**Symptoms:**
- API responses taking >10 seconds
- Search queries timing out
- Document processing slow

**Solutions:**

1. **Check OpenAI Rate Limits:**
   ```python
   from app.core.openai_client import get_openai_client
   client = get_openai_client()
   stats = client.get_usage_stats()
   print(stats)
   ```

2. **Optimize Chunk Size:**
   ```python
   # In .env
   CHUNK_SIZE=800  # Reduce from 1000
   CHUNK_OVERLAP=120
   ```

3. **Enable Caching:**
   ```python
   from app.core.embeddings_service import get_embeddings_service
   service = get_embeddings_service()
   service.use_cache = True
   ```

4. **Scale Pinecone:**
   - Upgrade to serverless or pod-based index
   - Increase replicas

5. **Monitor Metrics:**
   ```python
   from app.core.metrics import get_metrics_collector
   collector = get_metrics_collector()
   print(collector.get_metrics())
   ```

---

### Issue: Out of Memory (OOM)

**Symptoms:**
- Application crashes
- Docker container restarts
- "Memory limit exceeded" errors

**Solutions:**

1. **Increase Container Memory:**
   ```yaml
   # docker-compose.yml
   services:
     app:
       deploy:
         resources:
           limits:
             memory: 2G  # Increase from 1G
   ```

2. **Reduce Worker Count:**
   ```bash
   # .env
   WORKER_COUNT=2  # Reduce from 4
   ```

3. **Limit Batch Size:**
   ```python
   # In code
   batch_size = 50  # Reduce from 100
   ```

4. **Clear Cache:**
   ```python
   from app.core.embeddings_service import get_embeddings_service
   service = get_embeddings_service()
   service.clear_cache()
   ```

---

### Issue: Rate Limit Exceeded

**Symptoms:**
- "Rate limit exceeded" errors
- 429 status codes
- Requests being throttled

**Solutions:**

1. **Check Current Limits:**
   ```bash
   curl -I http://localhost:8000/api/search
   # Check X-RateLimit-Remaining header
   ```

2. **Increase Rate Limit:**
   ```python
   # In .env
   RATE_LIMIT_PER_MINUTE=120  # Increase from 60
   ```

3. **Implement Exponential Backoff:**
   ```python
   import time
   from tenacity import retry, wait_exponential
   
   @retry(wait=wait_exponential(multiplier=1, min=2, max=60))
   def api_call():
       # Your API call here
       pass
   ```

4. **Use Caching:**
   - Enable embeddings cache
   - Implement response caching with Redis

---

## Teams Bot Issues

### Issue: Bot Not Responding

**Symptoms:**
- Messages sent but no response
- Bot appears offline
- Commands not recognized

**Solutions:**

1. **Check Bot Endpoint:**
   ```bash
   curl http://localhost:8000/api/messages
   ```

2. **Verify Bot Credentials:**
   ```bash
   echo $MICROSOFT_APP_ID
   echo $MICROSOFT_APP_PASSWORD
   ```

3. **Check Logs:**
   ```bash
   docker logs ai-workplace-api | grep bot
   ```

4. **Test Bot Locally:**
   ```bash
   # Use Bot Framework Emulator
   # Connect to http://localhost:8000/api/messages
   ```

5. **Restart Bot Service:**
   ```bash
   docker-compose restart app
   ```

---

### Issue: Bot Commands Not Working

**Symptoms:**
- `/help` returns error
- Commands not recognized
- Invalid command messages

**Solutions:**

1. **Check Command Format:**
   - Ensure no extra spaces: `/help` not `/ help`
   - Commands are case-sensitive

2. **Clear Bot Cache:**
   ```
   /clear
   ```

3. **Verify Bot Permissions:**
   - Check Teams app manifest
   - Ensure bot has messaging permissions

4. **Update Bot:**
   ```bash
   git pull origin main
   docker-compose up -d --build
   ```

---

## Document Processing Issues

### Issue: PDF Upload Fails

**Symptoms:**
- "Failed to process PDF"
-Corrupted document errors
- Extraction errors

**Solutions:**

1. **Check File Size:**
   ```bash
   # Max 10MB by default
   ls -lh document.pdf
   ```

2. **Validate PDF:**
   ```bash
   # Install qpdf
   qpdf --check document.pdf
   ```

3. **Try Different PDF:**
   - Some PDFs have protection
   - Scanned PDFs need OCR
   - Try re-saving the PDF

4. **Increase Upload Limit:**
   ```python
   # In .env
   MAX_UPLOAD_SIZE=20971520  # 20MB
   ```

---

### Issue: Search Returns No Results

**Symptoms:**
- Empty search results
- No matches found
- Low relevance scores

**Solutions:**

1. **Check Document Count:**
   ```python
   from app.services.document_service import get_document_service
   service = get_document_service()
   count = await service.get_document_count()
   print(f"Documents: {count}")
   ```

2. **Verify Pinecone Has Data:**
   ```python
   from app.core.pinecone_service import create_pinecone_service
   service = create_pinecone_service()
   stats = service.get_index_stats()
   print(stats)
   ```

3. **Re-Index Documents:**
   ```python
   # Delete and re-upload documents
   service.delete(delete_all=True)
   # Re-upload your documents
   ```

4. **Adjust Search Parameters:**
   ```python
   # Increase top_k
   results = await search_service.search(query, top_k=10)
   ```

---

## Deployment Issues

### Issue: Azure App Service Won't Start

**Symptoms:**
- Application not responding
- 503 Service Unavailable
- Container startup failures

**Solutions:**

1. **Check Logs:**
   ```bash
   az webapp log tail \
     --name ai-workplace-automation \
     --resource-group ai-workplace-automation-rg
   ```

2. **Verify Environment Variables:**
   ```bash
   az webapp config appsettings list \
     --name ai-workplace-automation \
     --resource-group ai-workplace-automation-rg
   ```

3. **Check Container Health:**
   ```bash
   az webapp show \
     --name ai-workplace-automation \
     --resource-group ai-workplace-automation-rg \
     --query state
   ```

4. **Restart App Service:**
   ```bash
   az webapp restart \
     --name ai-workplace-automation \
     --resource-group ai-workplace-automation-rg
   ```

5. **Check Scaling:**
   ```bash
   # Ensure not scaled to 0
   az appservice plan show \
     --name ai-workplace-plan \
     --resource-group ai-workplace-automation-rg
   ```

---

### Issue: Container Registry Push Fails

**Symptoms:**
- "Access denied" errors
- Authentication failures
- Timeout during push

**Solutions:**

1. **Re-authenticate:**
   ```bash
   az acr login --name aiworkplaceacr
   ```

2. **Check Credentials:**
   ```bash
   az acr credential show --name aiworkplaceacr
   ```

3. **Verify Image Size:**
   ```bash
   docker images ai-workplace-automation
   # Should be < 2GB
   ```

4. **Use Admin Credentials:**
   ```bash
   az acr update -n aiworkplaceacr --admin-enabled true
   ```

---

## Performance Issues

### Issue: High CPU Usage

**Symptoms:**
- CPU constantly at 100%
- Slow responses
- Application lag

**Solutions:**

1. **Check Worker Count:**
   ```bash
   # Reduce workers if too many
   WORKER_COUNT=2
   ```

2. **Profile Application:**
   ```bash
   pip install py-spy
   py-spy top --pid <PID>
   ```

3. **Optimize Queries:**
   - Reduce top_k in searches
   - Use caching
   - Batch operations

4. **Scale Horizontally:**
   ```bash
   # Azure: Add more instances
   az monitor autoscale update \
     --count 3 \
     --resource-group ai-workplace-automation-rg
   ```

---

## Database & Storage Issues

### Issue: Redis Connection Failed

**Symptoms:**
- "Connection refused" errors
- Cache not working
- Session errors

**Solutions:**

1. **Check Redis Status:**
   ```bash
   docker ps | grep redis
   redis-cli ping  # Should return PONG
   ```

2. **Verify Connection:**
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379)
   r.ping()
   ```

3. **Restart Redis:**
   ```bash
   docker-compose restart redis
   ```

4. **Check Firewall:**
   - Ensure port 6379 is open
   - Validate network connectivity

---

## Security Issues

### Issue: JWT Token Invalid

**Symptoms:**
- 401 Unauthorized errors
- Token expired messages
- Authentication failures

**Solutions:**

1. **Check Token Expiration:**
   ```python
   from app.core.auth import verify_token
   payload = verify_token("your-token")
   print(payload)  # Check 'exp' field
   ```

2. **Refresh Token:**
   ```http
   POST /api/auth/refresh
   {
     "refresh_token": "your-refresh-token"
   }
   ```

3. **Verify Secret Key:**
   ```bash
   echo $SECRET_KEY
   # Should be set and consistent
   ```

4. **Generate New Token:**
   - Re-authenticate to get new token
   - Update client with new token

---

## Logging & Debugging

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG
```

### View Application Logs

```bash
# Docker
docker logs ai-workplace-api -f

# Local
tail -f logs/app.log

# Azure
az webapp log tail --name ai-workplace-automation
```

### Export Metrics

```python
from app.core.metrics import get_metrics_collector

collector = get_metrics_collector()
metrics = collector.get_metrics()

import json
print(json.dumps(metrics, indent=2))
```

---

## Getting Help

If you can't resolve the issue:

1. **Check GitHub Issues:** [Project Issues](https://github.com/Sridhar-19/AI-Powered-Workplace-Automation-System/issues)
2. **Review Logs:** Always include relevant logs when seeking help
3. **Contact Support:** Provide error messages and steps to reproduce
4. **Community:** Join discussions in project forums

---

## Useful Commands

```bash
# Health check
curl http://localhost:8000/health

# Test OpenAI
python -c "from app.core.openai_client import get_openai_client; client = get_openai_client(); print(client.chat_completion([{'role': 'user', 'content': 'test'}]))"

# Test Pinecone
python -c "from app.core.pinecone_service import create_pinecone_service; s = create_pinecone_service(); print(s.get_index_stats())"

# Run tests
pytest tests/ -v

# Clear cache
rm -rf __pycache__ .pytest_cache

# Rebuild Docker
docker-compose down -v
docker-compose up -d --build
```

---

For additional support, consult the [API Documentation](API.md), [Deployment Guide](DEPLOYMENT.md), or [User Guide](TEAMS_USER_GUIDE.md).
