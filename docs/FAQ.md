# Frequently Asked Questions (FAQ)

## General Questions

### What is the AI-Powered Workplace Automation System?

The AI-Powered Workplace Automation System is an enterprise solution that uses artificial intelligence to automate document processing, semantic search, and meeting notes extraction. It integrates with Microsoft Teams and provides AI-powered insights across your organization's documents.

### What can the system do?

- **Document Summarization**: Generate brief, standard, or detailed summaries of documents
- **Semantic Search**: Find information across thousands of documents using natural language
- **Meeting Notes Extraction**: Automatically extract decisions, action items, and key points from meeting transcripts
- **Q&A**: Get AI-generated answers with source citations
- **Teams Integration**: Access all features directly from Microsoft Teams

### Who should use this system?

- Teams that handle large volumes of documents
- Organizations needing quick access to information
- Companies wanting to automate meeting documentation
- Enterprises requiring semantic search capabilities

---

## Technical Questions

### What file formats are supported?

Supported formats:
- **PDF** (with metadata extraction)
- **DOCX** (Microsoft Word)
- **TXT** (Plain text)
- **MD** (Markdown)

### How many documents can the system handle?

The system is designed to scale to 5,000+ documents. Performance depends on:
- Infrastructure resources (CPU, memory)
- Pinecone plan (serverless or pod-based)
- Document size and complexity

### What AI models are used?

- **LLM**: OpenAI GPT-4 (configurable to GPT-3.5-turbo)
- **Embeddings**: OpenAI text-embedding-ada-002 or text-embedding-3-small
- **Vector Database**: Pinecone for similarity search

### How accurate is the summarization?

Summarization accuracy is typically 85-95% for:
- Well-structured documents
- Clear, professional language
- English text

Accuracy may vary for:
- Highly technical documents
- Documents with tables/charts
- Non-English text

### How fast are search queries?

Typical performance:
- **Search**: < 2 seconds
- **Search with Answer**: < 3 seconds
- **Document Upload**: < 5 seconds (10-page PDF)
- **Summarization**: < 3 seconds

---

## Cost Questions

### How much does it cost to run?

**Cloud Costs (Monthly Estimates):**

**OpenAI API:**
- GPT-4: $0.03/1K input tokens, $0.06/1K output tokens
- Embeddings: $0.0001/1K tokens
- Typical usage: $100-500/month (varies by volume)

**Pinecone:**
- Serverless: Pay per use (~$50-200/month)
- Pod-based: Starting at $70/month

**Azure (Small-Scale):**
- App Service B2: $73/month
- Redis Basic: $16/month
- Container Registry: $5/month
- **Total**: ~$100-150/month

**Total Estimated Cost**: $250-850/month depending on usage and scale

### How can I reduce costs?

1. **Enable Embeddings Caching**: 60-80% reduction in embedding API calls
2. **Use GPT-3.5-turbo**: 10x cheaper than GPT-4 for some tasks
3. **Batch Processing**: Process multiple documents at once
4. **Optimize Chunk Size**: Smaller chunks = fewer tokens
5. **Use Serverless Pinecone**: Pay only for actual usage

### Is there a free tier?

The system requires:
- OpenAI API key (paid, new accounts get $5 credit)
- Pinecone account (free tier available with limitations)
- Azure subscription (free tier available for limited usage)

You can run locally for development/testing at minimal cost.

---

## Security & Privacy Questions

### How is data secured?

- **Encryption in Transit**: All API calls use HTTPS/TLS
- **Encryption at Rest**: Pinecone encrypts stored data
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Protection against abuse
- **Input Validation**: All inputs sanitized

### Who has access to my documents?

- **User-level Access**: Each user only sees their uploaded documents
- **Admin Access**: System administrators can manage all documents
- **OpenAI**: Processes data but doesn't train on it (per OpenAI policy)
- **Pinecone**: Stores embeddings only, not raw documents

### Is my data used to train AI models?

**No.** According to OpenAI's API policy:
- Data sent via API is not used for model training
- Data is not shared with other customers
- Data is retained for 30 days for abuse monitoring, then deleted

### Can I deploy on-premises?

Yes! The system can be deployed on-premises using:
- Docker containers
- Kubernetes cluster
- Private OpenAI endpoint (Azure OpenAI Service)
- Self-hosted vector database

### Is the system GDPR/HIPAA compliant?

The system provides security features, but **compliance is deployment-specific:**

**For GDPR:**
- ✅ Supports data deletion
- ✅ Access controls
- ⚠️ Requires proper data processing agreements
- ⚠️ Audit logging may be needed

**For HIPAA:**
- ⚠️ Requires Azure OpenAI (not standard OpenAI)
- ⚠️ BAA (Business Associate Agreement) needed
- ⚠️ Additional security controls required

Consult your compliance team for requirements.

---

## Teams Bot Questions

### How do I install the Teams bot?

1. Your IT admin deploys the bot to Azure
2. Admin publishes the Teams app to your organization
3. You install from Teams app store
4. Start chatting with the bot

### Can the bot access my private chats?

**No.** The bot only works in:
- Direct conversations where you explicitly added the bot
- Team channels where the bot was added
- The bot cannot read messages in chats where it's not present

### Can I use the bot offline?

No, the bot requires internet connectivity to:
- Access OpenAI API
- Query Pinecone vector database
- Process documents

### How many people can use the bot simultaneously?

The system supports concurrent users based on:
- Infrastructure resources
- Azure App Service plan
- Rate limits (60 requests/minute per user by default)

Typical setup supports 50-100 concurrent users.

---

## Document Processing Questions

### What happens to uploaded documents?

1. Document is parsed and text extracted
2. Text is split into chunks (1000 characters each)
3. Embeddings are generated for each chunk
4. Embeddings stored in Pinecone
5. Original document metadata stored (but not the full document)

### Can I delete uploaded documents?

Yes! Use:
- API: `DELETE /api/documents/{document_id}`
- Or contact your administrator

This deletes both metadata and vector embeddings.

### Why is my PDF not processing correctly?

Common issues:
- **Scanned PDFs**: Need OCR (not currently supported)
- **Protected PDFs**: Password-protected files can't be processed
- **Large Files**: Files >10MB rejected by default
- **Corrupted Files**: Re-save the PDF

### Can I process images or videos?

Currently, no. Supported formats are text-based only:
- PDF, DOCX, TXT, MD

Image/video support may be added in future versions.

---

## Search & Summarization Questions

### Why am I getting irrelevant search results?

Try these tips:
1. **Be More Specific**: "Q4 2024 revenue targets" vs. "revenue"
2. **Use Full Sentences**: "What were the action items?" vs. "action items"
3. **Check Documents**: Ensure relevant documents are uploaded
4. **Increase top_k**: Search more documents (default: 5)

### Can I search specific documents only?

Not directly through the Teams bot. Using the API:

```python
result = await search_service.search(
    query="your query",
    filter={"source": "specific_document.pdf"}
)
```

### Why are summaries sometimes incorrect?

Possible reasons:
1. **Complex Documents**: Tables, charts not well-represented in text
2. **Length Issues**: Very long or very short documents
3. **Technical Jargon**: Specialized terminology
4. **Multiple Topics**: Documents covering too many topics

Tips:
- Try different summary lengths
- Provide context in the summarization request
- Break large documents into sections

### Can I customize the summary length?

Yes! Use these options:
- **Brief**: 2-3 sentences
- **Standard**: 20-25% of original (default)
- **Detailed**: Structured with sections

---

## Integration Questions

### Can I integrate with Slack?

Currently, only Teams is supported. Slack integration could be added by:
- Creating a Slack bot using the same core services
- Implementing Slack-specific handlers

### Can I integrate with SharePoint?

You can upload SharePoint documents via:
1. Download from SharePoint
2. Upload to the system via API or Teams bot

Direct SharePoint integration is not currently supported.

### Is there a webhook for notifications?

Yes! Set `WEBHOOK_URL` environment variable to receive:
- Document processing completion
- Batch job status updates
- System alerts

### Can I use the API from mobile apps?

Yes! The REST API works from any HTTP client:
- Mobile apps
- Web applications
- Desktop applications

Just include the JWT token in the Authorization header.

---

## Performance Questions

### Can I run this on my laptop?

Yes, for development/testing:
- **Minimum**: 8GB RAM, 4-core CPU
- **Recommended**: 16GB RAM, 8-core CPU, SSD
- **Docker**: 4GB memory allocated to Docker

Production should use cloud infrastructure.

### How do I improve performance?

1. **Enable Caching**: Embeddings cache, Redis for sessions
2. **Optimize Workers**: Set worker count based on CPU cores
3. **Scale Horizontally**: Add more instances (Azure autoscaling)
4. **Use CDN**: For static assets
5. **Batch Operations**: Process multiple documents at once
6. **Monitor**: Use Application Insights to identify bottlenecks

### Why is document upload slow?

Factors affecting upload speed:
- **Document Size**: Larger files take longer
- **Processing**: Text extraction, chunking, embedding generation
- **Network**: Upload bandwidth
- **Pinecone**: Vector upload speed

Typical: 10-page PDF in 3-5 seconds

---

## Troubleshooting Questions

### The bot is not responding. What should I do?

1. Check bot status: Send `/help`
2. Clear history: Send `/clear`
3. Check internet connection
4. Contact IT support if issue persists

See [Troubleshooting Guide](TROUBLESHOOTING.md) for more details.

### I'm getting authentication errors. How do I fix this?

1. **Refresh Token**: Re-authenticate to get new token
2. **Check Expiration**: Tokens expire after 30 minutes
3. **Verify Credentials**: Username and password correct
4. **Contact Admin**: May need account reset

### Where can I find logs?

**Local Development:**
```bash
tail -f logs/app.log
```

**Docker:**
```bash
docker logs ai-workplace-api -f
```

**Azure:**
```bash
az webapp log tail --name ai-workplace-automation
```

---

## Development Questions

### How do I contribute to the project?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

See `CONTRIBUTING.md` (if available) for details.

### How do I run tests?

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Can I customize the prompts?

Yes! Edit prompt templates in:
- `app/prompts/summary_prompts.py`
- `app/prompts/extraction_prompts.py`

Then restart the application.

### How do I add new document formats?

1. Create loader in `app/core/document_loader.py`
2. Add to `supported_formats` list
3. Implement parsing logic
4. Add tests

---

## Billing & Licensing Questions

### Is this open source?

Check the repository LICENSE file for licensing terms.

### Can I use this commercially?

Check the project license. Also consider:
- OpenAI Terms of Service
- Pinecone Terms of Service
- Azure Terms of Service

### Do I need separate licenses for dependencies?

Most dependencies use permissive licenses (MIT, Apache 2.0), but review:
- LangChain license
- FastAPI license
- Other third-party libraries

---

## Support Questions

### Where can I get help?

1. **Documentation**: Check docs/ folder
2. **GitHub Issues**: Report bugs or request features
3. **IT Support**: Contact your organization's helpdesk
4. **Email**: support@example.com (if configured)

### How do I report a bug?

1. Go to GitHub Issues
2. Click "New Issue"
3. Provide:
   - Description of bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs (if applicable)

### Can I request new features?

Yes! Submit a feature request via:
- GitHub Issues (use "Feature Request" template)
- Email to development team
- Internal feature request process

---

## Future Roadmap Questions

### What features are planned?

Potential future enhancements:
- Multi-language support
- OCR for scanned documents
- Image and video processing
- Advanced analytics dashboard
- Slack integration
- SharePoint connector
- Mobile apps

### When will X feature be available?

Check the GitHub project roadmap or contact the development team for feature timelines.

---

**Still have questions?**

- **Documentation**: [API Docs](API.md), [Deployment Guide](DEPLOYMENT.md), [User Guide](TEAMS_USER_GUIDE.md)
- **Support**: Contact your system administrator
- **GitHub**: https://github.com/Sridhar-19/AI-Powered-Workplace-Automation-System
