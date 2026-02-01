# Microsoft Teams Bot User Guide

## Welcome to AI Workplace Automation Bot! 👋

This guide will help you get started with the AI-powered Teams bot for document summarization, semantic search, and meeting notes extraction.

---

## Getting Started

### Adding the Bot to Teams

1. Open Microsoft Teams
2. Click **Apps** in the left sidebar
3. Search for **"AI Workplace Automation"**
4. Click **Add** to install the bot
5. Start a conversation with the bot

### First Interaction

When you first chat with the bot, you'll receive a welcome message with available commands. Type `/help` anytime to see the command list.

---

## Available Commands

### `/help` - Show Help

Displays all available commands and usage examples.

**Example:**
```
/help
```

---

### `/summarize` - Summarize Text

Generate an AI-powered summary of any text.

**Syntax:**
```
/summarize [your text here]
```

**Examples:**

**Brief Summary:**
```
/summarize This is a long article about artificial intelligence 
and machine learning. It covers topics like neural networks, 
deep learning, and natural language processing...
```

**Response:**
```
Summary

AI and ML article covering neural networks, deep learning, 
and NLP applications.

Method: single_pass
```

**Best Practices:**
- Works best with 100-5000 words
- Paste the full text after the command
- For very long documents (>5000 words), the bot will use map-reduce summarization

---

### `/search` - Search and Get Answers

Search across all uploaded documents and receive AI-generated answers.

**Syntax:**
```
/search [your question]
```

**Examples:**

```
/search What were the Q4 revenue targets?
```

**Response:**
```
Answer

Based on the quarterly financial report, Q4 revenue targets 
were set at $2.5M, representing a 15% increase from Q3. 
This target was approved during the planning meeting on Jan 10.

Sources (3 documents)
1. Q4_Financial_Report.pdf (relevance: 92%)
2. Planning_Meeting_Notes.docx (relevance: 85%)
3. Budget_Proposal.pdf (relevance: 78%)

Search time: 245ms
```

**Use Cases:**
- Find information across multiple documents
- Get quick answers to specific questions search for related content
- Discover insights from meeting notes and reports

**Tips:**
- Ask specific questions for better results
- Results are ranked by relevance
- Sources are cited automatically

---

### `/meeting` - Extract Meeting Notes

Automatically extract structured information from meeting transcripts.

**Syntax:**
```
/meeting [paste meeting transcript here]
```

**Example:**
```
/meeting Team discussed Q4 goals. Alice will prepare the presentation 
by Friday. Bob suggested increasing marketing budget by 15%. Team agreed 
to schedule a follow-up next Tuesday. Charlie raised concerns about timeline.
```

**Response:**
```
Meeting Notes Extracted

Decisions (1)
1. Agreed to increase marketing budget by 15%

Action Items (2)
1. Prepare presentation - Alice (Due: Friday)
2. Schedule follow-up meeting - Team (Due: Tuesday)

Key Points
• Discussed Q4 goals
• Charlie raised timeline concerns
• Budget increase approved
```

**What Gets Extracted:**
- ✅ **Decisions**: Important decisions made
- ✅ **Action Items**: Tasks with owners and due dates
- ✅ **Key Points**: Main discussion topics
- ✅ **Participants**: Attendees mentioned
- ✅ **Next Steps**: Follow-up actions

**Best Practices:**
- Include participant names in the transcript
- Mention due dates for action items
- Clear language works best

---

### `/clear` - Clear History

Clear your conversation history with the bot.

**Syntax:**
```
/clear
```

**Response:**
```
✅ Conversation history cleared!
```

**When to Use:**
- Starting a new topic
- Privacy concerns
- Bot seems confused by previous context

---

## Natural Conversation

You can also chat naturally with the bot without commands:

**Example:**
```
You: Can you help me summarize a document?
Bot: I can help you with:
- Document summarization (/summarize)
- Semantic search (/search)
- Meeting notes extraction (/meeting)

Type /help for more information!
```

---

## Best Practices

### For Summarization
✅ **Do:**
- Paste complete paragraphs
- Include context and details
- Use for documents 100-5000 words

❌ **Don't:**
- Send incomplete sentences
- Expect summaries of very short text (<50 words)
- Include sensitive personal information

### For Search
✅ **Do:**
- Ask specific, focused questions
- Use natural language
- Check source citations

❌ **Don't:**
- Ask multiple questions in one query
- Expect results if no documents uploaded
- Use very vague questions

### For Meeting Notes
✅ **Do:**
- Include full transcript
- Mention names and dates
- Use clear language

❌ **Don't:**
- Send partial conversations
- Expect perfect extraction from unclear notes
- Include irrelevant chat messages

---

## Common Use Cases

### 1. Quick Document Summary

**Scenario:** You receive a long email or document and need a quick summary.

```
/summarize [paste email/document]
```

### 2. Find Information Across Documents

**Scenario:** You need to find specific information from past reports.

```
/search What was our customer acquisition cost in Q3?
```

### 3. Action Items from Meetings

**Scenario:** After a meeting, extract action items to share with the team.

```
/meeting [paste meeting transcript or notes]
```

Copy the action items and share via Teams or email.

### 4. Research Assistant

**Scenario:** Research a topic across your organization's documents.

```
/search What are our sustainability initiatives?
```

---

## Tips for Success

1. **Be Specific**: The more specific your question, the better the answer
2. **Check Sources**: Always review the source documents for important decisions
3. **Iterate**: If you don't get the right answer, rephrase your question
4. **Use Commands**: Commands are faster than natural language
5. **Clear History**: Use `/clear` when switching topics

---

## Privacy & Security

- **Data Handling**: All data is processed securely and encrypted
- **Access Control**: Only you can see your conversation history
- **No Storage**: Individual messages are not permanently stored
- **Compliance**: System is compliant with enterprise security standards

---

## Limitations

- **Rate Limits**: 60 requests per minute per user
- **File Size**: Documents up to 10MB
- **Languages**: Best performance with English text
- **Response Time**: Most queries complete in 2-5 seconds

---

## Troubleshooting

### Bot Not Responding

**Solution:**
1. Check your internet connection
2. Try `/help` to test connectivity
3. Use `/clear` and try again
4. Contact IT support if issue persists

### Inaccurate Results

**Solution:**
1. Make your question more specific
2. Check if relevant documents are uploaded
3. Rephrase your query
4. Use `/search` instead of natural language

### Formatting Issues

**Solution:**
1. Ensure text is properly pasted
2. Remove special characters
3. Break very long text into sections

---

## FAQ

**Q: How many documents can I upload?**  
A: The system supports thousands of documents. Contact your admin for specific limits.

**Q: Can I delete my data?**  
A: Yes, contact your IT admin to delete your documents.

**Q: Does the bot learn from conversations?**  
A: No, the bot doesn't learn or store conversation history permanently.

**Q: Can I use the bot on mobile?**  
A: Yes! The bot works on Teams mobile app.

**Q: What file formats are supported?**  
A: PDF, DOCX, TXT, and Markdown files.

**Q: Is there a cost per query?**  
A: No cost to end users. Enterprise licenses cover usage.

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/h` + Tab | Auto-complete `/help` |
| `/s` + Tab | Auto-complete `/summarize` |
| `/m` + Tab | Auto-complete `/meeting` |

---

## Getting Help

- **In-Chat Help**: Type `/help`
- **IT Support**: Contact your IT helpdesk
- **Documentation**: Visit your company's internal wiki
- **Feedback**: Use the Teams feedback button

---

## Updates & New Features

The bot is regularly updated with new features. Recent additions:
- ✨ Faster search responses
- ✨ Improved meeting notes extraction
- ✨ Multi-language support (coming soon)

---

## Example Workflows

### Workflow 1: Weekly Team Meeting

1. Record or transcribe your meeting
2. Use `/meeting [transcript]` to extract notes
3. Share results with team
4. Store document for future `/search` queries

### Workflow 2: Document Research

1. Upload relevant documents to system
2. Use `/search` with specific questions
3. Review source citations
4. Compile findings into report

### Workflow 3: Email Management

1. Receive long email
2. Use `/summarize` to get key points
3. Take action based on summary
4. Archive original for searchability

---

**Happy Automating! 🚀**

For technical support or feature requests, contact your system administrator.
