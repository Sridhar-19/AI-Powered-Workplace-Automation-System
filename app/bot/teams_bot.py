"""
Microsoft Teams Bot implementation.
"""
import logging
from typing import Dict, Any, List
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import Activity, ActivityTypes, ChannelAccount, CardAction, ActionTypes

from app.services.summarization_service import get_summarization_service
from app.services.search_service import get_search_service
from app.chains.meeting_notes_chain import create_meeting_notes_chain

logger = logging.getLogger(__name__)


class TeamsBot(ActivityHandler):
    """
    Microsoft Teams Bot for AI-Powered Workplace Automation.
    """

    def __init__(self):
        super().__init__()
        self.summarization_service = get_summarization_service()
        self.search_service = get_search_service()
        self.meeting_notes_chain = create_meeting_notes_chain()
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming message activities.
        """
        try:
            text = turn_context.activity.text.strip()
            user_id = turn_context.activity.from_property.id

            # Initialize user session if needed
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    "conversation_history": [],
                    "last_command": None
                }

            # Handle commands
            if text.startswith('/'):
                await self._handle_command(turn_context, text, user_id)
            else:
                await self._handle_conversation(turn_context, text, user_id)

        except Exception as e:
            logger.error(f"Error in on_message_activity: {e}")
            await turn_context.send_activity(
                "Sorry, I encountered an error processing your request."
            )

    async def _handle_command(self, turn_context: TurnContext, text: str, user_id: str):
        """Handle bot commands."""
        command = text.split()[0].lower()
        args = text[len(command):].strip()

        if command == "/help":
            await self._command_help(turn_context)
        elif command == "/summarize":
            await self._command_summarize(turn_context, args)
        elif command == "/search":
            await self._command_search(turn_context, args)
        elif command == "/meeting":
            await self._command_meeting_notes(turn_context, args)
        elif command == "/clear":
            await self._command_clear(turn_context, user_id)
        else:
            await turn_context.send_activity(
                f"Unknown command: {command}. Type /help for available commands."
            )

    async def _command_help(self, turn_context: TurnContext):
        """Display help information."""
        help_text = """
**AI Workplace Automation Bot - Available Commands**

📝 **/summarize [text]** - Summarize the provided text
- Example: `/summarize [paste long text here]`

🔍 **/search [query]** - Search documents and get AI-generated answers
- Example: `/search What were the Q4 revenue targets?`

📅 **/meeting [transcript]** - Extract action items and decisions from meeting notes
- Example: `/meeting [paste meeting transcript]`

🗑️ **/clear** - Clear your conversation history

❓ **/help** - Show this help message

You can also just chat with me naturally, and I'll try to help!
"""
        await turn_context.send_activity(help_text)

    async def _command_summarize(self, turn_context: TurnContext, text: str):
        """Summarize provided text."""
        if not text:
            await turn_context.send_activity(
                "Please provide text to summarize. Usage: `/summarize [your text]`"
            )
            return

        try:
            # Send typing indicator
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )

            # Summarize
            result = await self.summarization_service.summarize_text(
                text=text,
                length="standard"
            )

            response = f"**Summary**\n\n{result['summary']}\n\n"
            response += f"_Method: {result['method']}_"

            await turn_context.send_activity(response)

        except Exception as e:
            logger.error(f"Error in summarize command: {e}")
            await turn_context.send_activity(
                "Sorry, I couldn't summarize the text. Please try again."
            )

    async def _command_search(self, turn_context: TurnContext, query: str):
        """Search documents and provide answer."""
        if not query:
            await turn_context.send_activity(
                "Please provide a search query. Usage: `/search [your question]`"
            )
            return

        try:
            # Send typing indicator
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )

            # Search with answer
            result = await self.search_service.search_with_answer(
                query=query,
                top_k=5
            )

            # Format response
            response = f"**Answer**\n\n{result['answer']}\n\n"
            response += f"**Sources** ({len(result['results'])} documents)\n"
            
            for i, doc in enumerate(result['results'][:3], 1):
                score = int(doc.score * 100)
                source = doc.metadata.get('source', 'Unknown')
                response += f"{i}. {source} (relevance: {score}%)\n"

            response += f"\n_Search time: {result['search_time_ms']:.0f}ms_"

            await turn_context.send_activity(response)

        except Exception as e:
            logger.error(f"Error in search command: {e}")
            await turn_context.send_activity(
                "Sorry, I couldn't complete the search. Please try again."
            )

    async def _command_meeting_notes(self, turn_context: TurnContext, text: str):
        """Extract meeting notes."""
        if not text:
            await turn_context.send_activity(
                "Please provide meeting transcript. Usage: `/meeting [transcript]`"
            )
            return

        try:
            # Send typing indicator
            await turn_context.send_activity(
                Activity(type=ActivityTypes.typing)
            )

            # Extract meeting notes
            result = self.meeting_notes_chain.extract_meeting_notes(text)

            # Format response
            response = "**Meeting Notes Extracted**\n\n"

            if result.get('decisions'):
                response += f"**Decisions** ({len(result['decisions'])})\n"
                for i, decision in enumerate(result['decisions'][:5], 1):
                    response += f"{i}. {decision['decision']}\n"
                response += "\n"

            if result.get('action_items'):
                response += f"**Action Items** ({len(result['action_items'])})\n"
                for i, item in enumerate(result['action_items'][:5], 1):
                    owner = item.get('owner', 'Unassigned')
                    response += f"{i}. {item['task']} - {owner}\n"
                response += "\n"

            if result.get('key_points'):
                response += f"**Key Points**\n"
                for point in result['key_points'][:3]:
                    response += f"• {point}\n"

            await turn_context.send_activity(response)

        except Exception as e:
            logger.error(f"Error in meeting notes command: {e}")
            await turn_context.send_activity(
                "Sorry, I couldn't extract meeting notes. Please try again."
            )

    async def _command_clear(self, turn_context: TurnContext, user_id: str):
        """Clear user conversation history."""
        if user_id in self.user_sessions:
            self.user_sessions[user_id] = {
                "conversation_history": [],
                "last_command": None
            }
        await turn_context.send_activity("✅ Conversation history cleared!")

    async def _handle_conversation(self, turn_context: TurnContext, text: str, user_id: str):
        """Handle natural conversation."""
        # For now, provide a simple response
        # In production, this could use the QA chain with conversation history
        response = (
            f"I received your message: \"{text[:50]}...\"\n\n"
            "I can help you with:\n"
            "- Document summarization (/summarize)\n"
            "- Semantic search (/search)\n"
            "- Meeting notes extraction (/meeting)\n\n"
            "Type /help for more information!"
        )
        await turn_context.send_activity(response)

    async def on_members_added_activity(
        self,
        members_added: List[ChannelAccount],
        turn_context: TurnContext
    ):
        """
        Handle new members added to conversation.
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_message = (
                    "👋 **Welcome to AI Workplace Automation Bot!**\n\n"
                    "I can help you with:\n"
                    "📝 Document summarization\n"
                    "🔍 Semantic search across documents\n"
                    "📅 Meeting notes extraction\n\n"
                    "Type **/help** to see all available commands!"
                )
                await turn_context.send_activity(welcome_message)

    async def on_conversation_update_activity(self, turn_context: TurnContext):
        """
        Handle conversation update events.
        """
        logger.info(f"Conversation update: {turn_context.activity.type}")
        await super().on_conversation_update_activity(turn_context)


def create_teams_bot() -> TeamsBot:
    """Factory function to create Teams bot."""
    return TeamsBot()
