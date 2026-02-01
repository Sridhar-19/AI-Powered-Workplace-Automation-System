"""
Prompt templates for extracting information from meeting notes and documents.
"""
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional


# Meeting notes extraction prompt
MEETING_NOTES_EXTRACTION_TEMPLATE = """You are an expert at extracting structured information from meeting transcripts.

Analyze the following meeting transcript and extract:

1. **Decisions Made**: Key decisions that were finalized
2. **Action Items**: Tasks with assigned owners and due dates (if mentioned)
3. **Key Discussion Points**: Important topics discussed
4. **Participants**: People mentioned in the meeting (if identifiable)
5. **Next Steps**: Planned follow-up actions

Format your response as a structured JSON with the following schema:
{{
  "decisions": [
    {{"decision": "...", "context": "...", "impact": "..."}}
  ],
  "action_items": [
    {{"task": "...", "owner": "...", "due_date": "...", "priority": "..."}}
  ],
  "key_points": ["...", "..."],
  "participants": ["...", "..."],
  "next_steps": ["...", "..."]
}}

Meeting Transcript:
{text}

Extracted Information (JSON):"""

meeting_notes_prompt = PromptTemplate(
    input_variables=["text"],
    template=MEETING_NOTES_EXTRACTION_TEMPLATE,
)


# Action item extraction prompt
ACTION_ITEM_EXTRACTION_TEMPLATE = """You are an expert at identifying action items from text.

Extract all action items from the following text. For each action item, identify:
- The task or action to be completed
- Who is responsible (if mentioned)
- When it should be done (if mentioned)
- Priority level (high/medium/low based on context)

Return the results as a JSON array:
[
  {{"task": "...", "owner": "...", "due_date": "...", "priority": "..."}},
  ...
]

Text:
{text}

Action Items (JSON):"""

action_item_prompt = PromptTemplate(
    input_variables=["text"],
    template=ACTION_ITEM_EXTRACTION_TEMPLATE,
)


# Decision extraction prompt
DECISION_EXTRACTION_TEMPLATE = """You are an expert at identifying key decisions from meeting notes and documents.

Extract all important decisions from the following text. For each decision, identify:
- What was decided
- The context or reasoning behind the decision
- The potential impact or implications

Return the results as a JSON array:
[
  {{"decision": "...", "context": "...", "impact": "..."}},
  ...
]

Text:
{text}

Decisions (JSON):"""

decision_extraction_prompt = PromptTemplate(
    input_variables=["text"],
    template=DECISION_EXTRACTION_TEMPLATE,
)


# Key points extraction prompt
KEY_POINTS_EXTRACTION_TEMPLATE = """You are an expert at identifying the most important points from text.

Extract the {num_points} most important key points from the following text. 
Return them as a JSON array of strings, ordered by importance.

Text:
{text}

Key Points (JSON array):"""

key_points_prompt = PromptTemplate(
    input_variables=["text", "num_points"],
    template=KEY_POINTS_EXTRACTION_TEMPLATE,
)


# Sentiment analysis prompt (optional)
SENTIMENT_ANALYSIS_TEMPLATE = """Analyze the sentiment and tone of the following text.

Provide:
1. Overall sentiment (positive/neutral/negative)
2. Confidence score (0-100%)
3. Key sentiment indicators (words or phrases that indicate the sentiment)
4. Tone (professional/casual/urgent/etc.)

Return as JSON:
{{
  "sentiment": "...",
  "confidence": ...,
  "indicators": ["...", "..."],
  "tone": "..."
}}

Text:
{text}

Sentiment Analysis (JSON):"""

sentiment_analysis_prompt = PromptTemplate(
    input_variables=["text"],
    template=SENTIMENT_ANALYSIS_TEMPLATE,
)


# Entity extraction prompt
ENTITY_EXTRACTION_TEMPLATE = """Extract all named entities from the following text and categorize them.

Categories:
- People: Names of individuals
- Organizations: Company names, teams, departments
- Dates: Specific dates or time periods
- Locations: Places, cities, countries
- Products: Product names, features, services
- Numbers: Important metrics, quantities, percentages

Return as JSON:
{{
  "people": ["...", "..."],
  "organizations": ["...", "..."],
  "dates": ["...", "..."],
  "locations": ["...", "..."],
  "products": ["...", "..."],
  "numbers": ["...", "..."]
}}

Text:
{text}

Extracted Entities (JSON):"""

entity_extraction_prompt = PromptTemplate(
    input_variables=["text"],
    template=ENTITY_EXTRACTION_TEMPLATE,
)


# Question generation prompt (for creating FAQs)
QUESTION_GENERATION_TEMPLATE = """Based on the following document, generate {num_questions} relevant questions that it answers.

These questions should:
- Cover the main topics and key information
- Be clear and specific
- Be questions that someone might actually ask about this content

Return as a JSON array of strings:
["Question 1?", "Question 2?", ...]

Document:
{text}

Generated Questions (JSON):"""

question_generation_prompt = PromptTemplate(
    input_variables=["text", "num_questions"],
    template=QUESTION_GENERATION_TEMPLATE,
)


def get_extraction_prompt(extraction_type: str) -> PromptTemplate:
    """
    Get the appropriate extraction prompt based on type.
    
    Args:
        extraction_type: Type of extraction (meeting_notes, action_items, 
                        decisions, key_points, sentiment, entities, questions)
        
    Returns:
        Appropriate PromptTemplate
    """
    prompts = {
        "meeting_notes": meeting_notes_prompt,
        "action_items": action_item_prompt,
        "decisions": decision_extraction_prompt,
        "key_points": key_points_prompt,
        "sentiment": sentiment_analysis_prompt,
        "entities": entity_extraction_prompt,
        "questions": question_generation_prompt,
    }
    
    return prompts.get(extraction_type, meeting_notes_prompt)
