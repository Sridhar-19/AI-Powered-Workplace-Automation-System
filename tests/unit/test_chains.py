"""
Unit tests for LangChain chains.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.chains.summarization_chain import SummarizationChain, create_summarization_chain
from app.chains.meeting_notes_chain import MeetingNotesChain, create_meeting_notes_chain
from app.chains.qa_chain import QAChain, create_qa_chain


class TestSummarizationChain:
    """Tests for summarization chain."""

    def test_create_summarization_chain(self):
        """Test chain creation."""
        chain = create_summarization_chain()
        assert isinstance(chain, SummarizationChain)
        assert chain.llm is not None

    def test_estimate_tokens(self):
        """Test token estimation."""
        chain = create_summarization_chain()
        text = "This is a test" * 100
        tokens = chain._estimate_tokens(text)
        assert tokens > 0
        assert tokens < len(text)  # Should be less than character count

    @patch('app.chains.summarization_chain.LLMChain')
    def test_single_pass_summarization(self, mock_llm_chain):
        """Test single-pass summarization."""
        # Mock LLM response
        mock_chain_instance = Mock()
        mock_chain_instance.invoke.return_value = {
            "text": "This is a summary of the document."
        }
        mock_llm_chain.return_value = mock_chain_instance

        chain = create_summarization_chain()
        
        # Short text that won't trigger map-reduce
        text = "This is a short document that needs summarization."
        
        result = chain.summarize(text, length="brief")
        
        assert "summary" in result
        assert result["length"] == "brief"
        assert result["method"] in ["single_pass", "map_reduce"]


class TestMeetingNotesChain:
    """Tests for meeting notes chain."""

    def test_create_meeting_notes_chain(self):
        """Test chain creation."""
        chain = create_meeting_notes_chain()
        assert isinstance(chain, MeetingNotesChain)

    @patch('app.chains.meeting_notes_chain.LLMChain')
    def test_extract_meeting_notes(self, mock_llm_chain):
        """Test meeting notes extraction."""
        # Mock LLM response with valid JSON
        mock_response = {
            "text": '''{
                "decisions": [{"decision": "Approved budget", "context": "Q4 planning"}],
                "action_items": [{"task": "Prepare report", "owner": "John"}],
                "key_points": ["Budget discussion", "Timeline review"],
                "participants": ["Alice", "Bob"],
                "next_steps": ["Schedule follow-up"]
            }'''
        }
        
        mock_chain_instance = Mock()
        mock_chain_instance.invoke.return_value = mock_response
        mock_llm_chain.return_value = mock_chain_instance

        chain = create_meeting_notes_chain()
        
        # Test extraction
        text = "Meeting notes: We discussed the budget and decided to increase it by 15%."
        result = chain.extract_meeting_notes(text)
        
        assert "decisions" in result
        assert "action_items" in result


class TestQAChain:
    """Tests for QA chain."""

    def test_create_qa_chain(self):
        """Test chain creation."""
        chain = create_qa_chain()
        assert isinstance(chain, QAChain)

    @patch('app.chains.qa_chain.LLMChain')
    def test_answer_question(self, mock_llm_chain):
        """Test question answering."""
        # Mock LLM response
        mock_chain_instance = Mock()
        mock_chain_instance.invoke.return_value = {
            "text": "The Q4 revenue target was $2.5M."
        }
        mock_llm_chain.return_value = mock_chain_instance

        chain = create_qa_chain()
        
        result = chain.answer_question(
            question="What was the Q4 revenue target?",
            context="Q4 revenue targets were set at $2.5M based on market analysis."
        )
        
        assert "answer" in result
        assert "question" in result

    def test_conversation_history(self):
        """Test conversation history management."""
        chain = create_qa_chain()
        
        # Initially empty
        assert len(chain.get_history()) == 0
        
        # Clear should work
        chain.clear_history()
        assert len(chain.get_history()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
