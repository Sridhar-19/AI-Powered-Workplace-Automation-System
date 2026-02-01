# API Documentation

## Overview

The AI-Powered Workplace Automation System provides RESTful APIs for document management, summarization, semantic search, and Microsoft Teams integration.

**Base URL:** `http://localhost:8000` (development)  
**API Version:** v1  
**Authentication:** JWT Bearer Token

---

## Authentication

### Obtain Access Token

```http
POST /api/auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Token

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Document Management

### Upload Document

Upload and process a document for search and summarization.

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary data>
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "filename": "quarterly_report.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "status": "completed",
  "num_pages": 10,
  "num_chunks": 25,
  "upload_date": "2024-01-15T10:30:00Z"
}
```

### Get Document

Retrieve document metadata.

```http
GET /api/documents/{document_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "filename": "quarterly_report.pdf",
  "status": "completed",
  "num_chunks": 25,
  "upload_date": "2024-01-15T10:30:00Z"
}
```

### List Documents

Get paginated list of documents.

```http
GET /api/documents?skip=0&limit=20
Authorization: Bearer <token>
```

**Response:**
```json
{
  "documents": [
    {
      "document_id": "doc_abc123",
      "filename": "quarterly_report.pdf",
      "status": "completed"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### Delete Document

Delete a document and its embeddings.

```http
DELETE /api/documents/{document_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

---

## Summarization

### Summarize Text

Generate a summary from raw text.

```http
POST /api/summarize/text
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Long document content here...",
  "length": "standard",
  "document_type": "general"
}
```

**Parameters:**
- `length`: "brief" | "standard" | "detailed"
- `document_type`: "general" | "technical"

**Response:**
```json
{
  "summary": "This document discusses quarterly financial results...",
  "length": "standard",
  "method": "single_pass",
  "num_chunks": null
}
```

### Summarize Document

Summarize a previously uploaded document.

```http
POST /api/summarize/document
Authorization: Bearer <token>
Content-Type: application/json

{
  "document_id": "doc_abc123",
  "length": "brief"
}
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "summary": "Brief summary of the document...",
  "length": "brief",
  "generated_at": "2024-01-15T10:35:00Z"
}
```

### Batch Summarization

Start a batch summarization job.

```http
POST /api/summarize/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "document_ids": ["doc_123", "doc_456", "doc_789"],
  "length": "standard"
}
```

**Response:**
```json
{
  "job_id": "job_xyz789",
  "status": "pending",
  "total_documents": 3
}
```

### Get Job Status

Check batch job status.

```http
GET /api/summarize/jobs/{job_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "job_id": "job_xyz789",
  "status": "processing",
  "total": 3,
  "completed": 1,
  "results": [...]
}
```

---

## Semantic Search

### Search Documents

Perform semantic search across all documents.

```http
POST /api/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What were the Q4 revenue targets?",
  "top_k": 5,
  "include_metadata": true
}
```

**Response:**
```json
{
  "query": "What were the Q4 revenue targets?",
  "results": [
    {
      "document_id": "doc_123_chunk_5",
      "score": 0.89,
      "text": "Q4 revenue targets were set at $2.5M...",
      "metadata": {
        "source": "quarterly_report.pdf",
        "page": 3
      }
    }
  ],
  "total_results": 5,
  "search_time_ms": 145.2
}
```

### Search with Answer

Get AI-generated answer along with search results.

```http
POST /api/search/answer
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What were the Q4 revenue targets?",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "What were the Q4 revenue targets?",
  "answer": "Based on the quarterly report, Q4 revenue targets were set at $2.5M, representing a 15% increase from Q3.",
  "results": [...],
  "search_time_ms": 245.8
}
```

### Find Similar Documents

Find documents similar to a given document.

```http
POST /api/search/similar
Authorization: Bearer <token>
Content-Type: application/json

{
  "document_id": "doc_abc123",
  "top_k": 5
}
```

**Response:**
```json
{
  "source_document_id": "doc_abc123",
  "similar_documents": [
    {
      "document_id": "doc_xyz789",
      "score": 0.92,
      "text": "...",
      "metadata": {...}
    }
  ]
}
```

---

## Meeting Notes

### Extract Meeting Notes

Extract structured information from meeting transcripts.

```http
POST /api/meetings/extract
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Meeting transcript here...",
  "meeting_title": "Q4 Planning Meeting"
}
```

**Response:**
```json
{
  "title": "Q4 Planning Meeting",
  "participants": ["Alice", "Bob", "Charlie"],
  "decisions": [
    {
      "decision": "Approved budget increase of 15%",
      "context": "To support expanded marketing campaign",
      "impact": "Expected 20% increase in customer acquisition"
    }
  ],
  "action_items": [
    {
      "task": "Prepare Q4 presentation",
      "owner": "John Doe",
      "due_date": "2024-03-15",
      "priority": "high",
      "status": "pending"
    }
  ],
  "key_points": [
    "Discussed Q4 targets",
    "Reviewed budget allocation"
  ],
  "next_steps": [
    "Schedule follow-up meeting",
    "Distribute action items"
  ]
}
```

---

## Health Check

### System Health

Check system health and status.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:45:00Z"
}
```

---

## Rate Limits

- **Rate Limit:** 60 requests per minute per IP
- **Burst:** Up to 100 requests

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": 60
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "detail": "Additional error details",
  "timestamp": "2024-01-15T10:45:00Z"
}
```

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | BAD_REQUEST | Invalid request parameters |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 413 | PAYLOAD_TOO_LARGE | Request entity too large (>10MB) |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

---

## SDK Examples

### Python

```python
import requests

# Authenticate
response = requests.post(
    "http://localhost:8000/api/auth/token",
    json={"username": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Upload document
with open("report.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f}
    )
doc = response.json()

# Search with answer
response = requests.post(
    "http://localhost:8000/api/search/answer",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "What were the Q4 targets?", "top_k": 5}
)
result = response.json()
print(result["answer"])
```

### JavaScript

```javascript
// Authenticate
const authResponse = await fetch('http://localhost:8000/api/auth/token', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'user@example.com',
    password: 'password'
  })
});
const {access_token} = await authResponse.json();

// Search
const searchResponse = await fetch('http://localhost:8000/api/search/answer', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'What were the Q4 targets?',
    top_k: 5
  })
});
const result = await searchResponse.json();
console.log(result.answer);
```

---

## Webhooks

### Document Processing Complete

Receive notifications when document processing completes.

**Endpoint Configuration:** Set in environment variable `WEBHOOK_URL`

**Payload:**
```json
{
  "event": "document.processed",
  "document_id": "doc_abc123",
  "status": "completed",
  "timestamp": "2024-01-15T10:45:00Z"
}
```

---

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
```
GET /openapi.json
```

Interactive documentation:
```
GET /docs
```

---

## Support

For API support and questions:
- **Email:** support@example.com
- **GitHub Issues:** https://github.com/Sridhar-19/AI-Powered-Workplace-Automation-System/issues
