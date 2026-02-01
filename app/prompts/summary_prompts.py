"""
Prompt templates for document summarization.
"""
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate


# Brief summary prompt template
BRIEF_SUMMARY_TEMPLATE = """You are an expert at creating concise summaries of documents.

Given the following document, create a brief summary (2-3 sentences) that captures the most important points:

Document:
{text}

Brief Summary:"""

brief_summary_prompt = PromptTemplate(
    input_variables=["text"],
    template=BRIEF_SUMMARY_TEMPLATE,
)


# Standard summary prompt template
STANDARD_SUMMARY_TEMPLATE = """You are an expert at creating comprehensive summaries of documents.

Your task is to create a well-structured summary of the following document. The summary should:
- Capture the main ideas and key points
- Maintain the logical flow of the original document
- Be approximately 20-25% of the original length
- Be written in clear, concise language

Document:
{text}

Comprehensive Summary:"""

standard_summary_prompt = PromptTemplate(
    input_variables=["text"],
    template=STANDARD_SUMMARY_TEMPLATE,
)


# Detailed summary prompt template
DETAILED_SUMMARY_TEMPLATE = """You are an expert at creating detailed, structured summaries of documents.

Create a detailed summary of the following document with these sections:

1. **Executive Summary**: One paragraph overview
2. **Key Points**: Bullet points of main ideas
3. **Important Details**: Significant facts, figures, and findings
4. **Conclusions/Recommendations**: If applicable

Document:
{text}

Detailed Summary:"""

detailed_summary_prompt = PromptTemplate(
    input_variables=["text"],
    template=DETAILED_SUMMARY_TEMPLATE,
)


# Map-reduce summary prompts for long documents
MAP_SUMMARY_TEMPLATE = """You are creating a summary of a section of a larger document.

Summarize the key points from this section concisely:

{text}

Section Summary:"""

map_summary_prompt = PromptTemplate(
    input_variables=["text"],
    template=MAP_SUMMARY_TEMPLATE,
)


REDUCE_SUMMARY_TEMPLATE = """You are combining multiple section summaries into a cohesive final summary.

Given these section summaries from a document, create a unified summary that:
- Combines and synthesizes the information
- Eliminates redundancy
- Maintains logical flow
- Preserves all important information

Section Summaries:
{text}

Final Combined Summary:"""

reduce_summary_prompt = PromptTemplate(
    input_variables=["text"],
    template=REDUCE_SUMMARY_TEMPLATE,
)


# Technical document summary template
TECHNICAL_SUMMARY_TEMPLATE = """You are an expert at summarizing technical documents.

Create a structured summary of this technical document including:

1. **Purpose/Objective**: What is this document about?
2. **Technical Details**: Key technical information, specifications, or methodologies
3. **Results/Findings**: Main outcomes or conclusions
4. **Action Items**: Any recommendations or next steps

Document:
{text}

Technical Summary:"""

technical_summary_prompt = PromptTemplate(
    input_variables=["text"],
    template=TECHNICAL_SUMMARY_TEMPLATE,
)


# Few-shot examples for better summarization
summary_examples = [
    {
        "text": "The quarterly sales report shows revenue increased by 15% compared to Q3. The marketing campaign launched in September contributed to a 25% increase in new customer acquisitions. However, operating expenses also increased by 8% due to expanded staffing. The product team delivered three major feature releases. Overall, the quarter exceeded targets despite market headwinds.",
        "summary": "Q4 revenue grew 15% year-over-year with a 25% increase in new customers driven by the September marketing campaign. While operating expenses rose 8% from expanded staffing, the quarter exceeded targets with three major product releases despite market challenges.",
    },
    {
        "text": "The new authentication system will replace the legacy OAuth implementation. Implementation requires updating the user database schema, migrating existing tokens, and updating all API endpoints. The rollout plan includes a two-week beta testing phase with selected customers, followed by a phased migration of 10% of users per day. Rollback procedures are in place if issues arise. The project timeline is 6 weeks with Go-Live scheduled for March 15.",
        "summary": "New authentication system replacing OAuth requires database schema updates, token migration, and API endpoint modifications. Six-week timeline includes two-week beta testing and phased user migration (10% daily) with rollback procedures. Go-Live: March 15.",
    },
]

summary_example_template = PromptTemplate(
    input_variables=["text", "summary"],
    template="Document: {text}\nSummary: {summary}",
)

few_shot_summary_prompt = FewShotPromptTemplate(
    examples=summary_examples,
    example_prompt=summary_example_template,
    prefix="You are an expert at creating concise, informative summaries. Here are some examples:\n",
    suffix="\nNow create a summary for this document:\n\nDocument: {text}\nSummary:",
    input_variables=["text"],
)


def get_summary_prompt(length: str = "standard", document_type: str = "general") -> PromptTemplate:
    """
    Get the appropriate summary prompt based on length and document type.
    
    Args:
        length: 'brief', 'standard', or 'detailed'
        document_type: 'general', 'technical', or 'few-shot'
        
    Returns:
        Appropriate PromptTemplate
    """
    if document_type == "technical":
        return technical_summary_prompt
    
    if document_type == "few-shot":
        return few_shot_summary_prompt
    
    if length == "brief":
        return brief_summary_prompt
    elif length == "detailed":
        return detailed_summary_prompt
    else:
        return standard_summary_prompt
