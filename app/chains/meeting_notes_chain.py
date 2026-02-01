"""
LangChain chain for meeting notes extraction.
"""
import logging
import json
from typing import Dict, Any, List, Optional
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from pydantic import BaseModel, Field

from app.config import get_settings
from app.prompts.extraction_prompts import (
    meeting_notes_prompt,
    action_item_prompt,
    decision_extraction_prompt,
)

logger = logging.getLogger(__name__)
settings = get_settings()


# Pydantic models for structured output
class ActionItem(BaseModel):
    """Action item extracted from meeting notes."""
    task: str = Field(description="The task or action to be completed")
    owner: Optional[str] = Field(default=None, description="Person responsible")
    due_date: Optional[str] = Field(default=None, description="Due date if mentioned")
    priority: Optional[str] = Field(default="medium", description="Priority level")


class Decision(BaseModel):
    """Decision extracted from meeting notes."""
    decision: str = Field(description="The decision that was made")
    context: Optional[str] = Field(default=None, description="Context or reasoning")
    impact: Optional[str] = Field(default=None, description="Impact or implications")


class MeetingNotesExtraction(BaseModel):
    """Complete meeting notes extraction."""
    decisions: List[Decision] = Field(default_factory=list, description="Decisions made")
    action_items: List[ActionItem] = Field(default_factory=list, description="Action items")
    key_points: List[str] = Field(default_factory=list, description="Key discussion points")
    participants: List[str] = Field(default_factory=list, description="Meeting participants")
    next_steps: List[str] = Field(default_factory=list, description="Next steps")


class MeetingNotesChain:
    """
    Chain for extracting structured information from meeting notes.
    """

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.1,
    ):
        """
        Initialize the meeting notes extraction chain.
        
        Args:
            model: OpenAI model to use
            temperature: Sampling temperature (lower for more structured output)
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY,
        )

    def extract_meeting_notes(self, text: str) -> Dict[str, Any]:
        """
        Extract structured information from meeting notes.
        
        Args:
            text: Meeting transcript or notes
            
        Returns:
            Dictionary with extracted information
        """
        try:
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=meeting_notes_prompt)
            
            # Generate extraction
            result = chain.invoke({"text": text})
            output = result.get("text", "").strip()
            
            # Parse JSON output
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON, attempting to fix: {e}")
                # Try to extract JSON from markdown code blocks
                if "```json" in output:
                    output = output.split("```json")[1].split("```")[0].strip()
                elif "```" in output:
                    output = output.split("```")[1].split("```")[0].strip()
                parsed = json.loads(output)
            
            # Structure the output
            extraction = {
                "decisions": parsed.get("decisions", []),
                "action_items": parsed.get("action_items", []),
                "key_points": parsed.get("key_points", []),
                "participants": parsed.get("participants", []),
                "next_steps": parsed.get("next_steps", []),
            }
            
            logger.info(
                f"Extracted {len(extraction['decisions'])} decisions, "
                f"{len(extraction['action_items'])} action items"
            )
            
            return extraction
            
        except Exception as e:
            logger.error(f"Error extracting meeting notes: {e}")
            raise

    def extract_action_items(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract only action items from text.
        
        Args:
            text: Text to extract action items from
            
        Returns:
            List of action item dictionaries
        """
        try:
            chain = LLMChain(llm=self.llm, prompt=action_item_prompt)
            result = chain.invoke({"text": text})
            output = result.get("text", "").strip()
            
            # Parse JSON
            try:
                action_items = json.loads(output)
            except json.JSONDecodeError:
                if "```json" in output:
                    output = output.split("```json")[1].split("```")[0].strip()
                elif "```" in output:
                    output = output.split("```")[1].split("```")[0].strip()
                action_items = json.loads(output)
            
            logger.info(f"Extracted {len(action_items)} action items")
            return action_items
            
        except Exception as e:
            logger.error(f"Error extracting action items: {e}")
            raise

    def extract_decisions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract only decisions from text.
        
        Args:
            text: Text to extract decisions from
            
        Returns:
            List of decision dictionaries
        """
        try:
            chain = LLMChain(llm=self.llm, prompt=decision_extraction_prompt)
            result = chain.invoke({"text": text})
            output = result.get("text", "").strip()
            
            # Parse JSON
            try:
                decisions = json.loads(output)
            except json.JSONDecodeError:
                if "```json" in output:
                    output = output.split("```json")[1].split("```")[0].strip()
                elif "```" in output:
                    output = output.split("```")[1].split("```")[0].strip()
                decisions = json.loads(output)
            
            logger.info(f"Extracted {len(decisions)} decisions")
            return decisions
            
        except Exception as e:
            logger.error(f"Error extracting decisions: {e}")
            raise


def create_meeting_notes_chain(
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.1,
) -> MeetingNotesChain:
    """
    Factory function to create a meeting notes extraction chain.
    
    Args:
        model: OpenAI model to use
        temperature: Sampling temperature
        
    Returns:
        MeetingNotesChain instance
    """
    return MeetingNotesChain(model=model, temperature=temperature)
