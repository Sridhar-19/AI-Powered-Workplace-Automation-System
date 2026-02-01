"""
Bot configuration and adapter setup.
"""
import logging
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BotConfig:
    """Bot configuration and adapter."""

    def __init__(self):
        # Bot Framework adapter settings
        self.adapter_settings = BotFrameworkAdapterSettings(
            app_id=settings.microsoft_app_id or "",
            app_password=settings.microsoft_app_password or ""
        )
        
        # Create adapter
        self.adapter = BotFrameworkAdapter(self.adapter_settings)
        
        # Error handler
        async def on_error(context, error):
            logger.error(f"Bot error: {error}")
            await context.send_activity("Sorry, something went wrong!")
        
        self.adapter.on_turn_error = on_error

    def get_adapter(self) -> BotFrameworkAdapter:
        """Get bot framework adapter."""
        return self.adapter


# Global bot config instance
_bot_config = None


def get_bot_config() -> BotConfig:
    """Get or create bot configuration."""
    global _bot_config
    if _bot_config is None:
        _bot_config = BotConfig()
    return _bot_config
