from telegram import Bot
from telegram.constants import ChatAction
from typing import AsyncIterator
from core.channels.base import BaseChannel
from config.settings import get_settings
import logging

logger = logging.getLogger(__name__)


class TelegramChannel(BaseChannel):
    """
    Telegram channel adapter.
    Handles typing indicators and streaming responses via Telegram Bot API.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.bot = Bot(token=settings.telegram_token)

    async def send_typing(self, user_id: str) -> None:
        """
        Show 'typing...' indicator in Telegram chat.
        Lasts ~5 seconds — call repeatedly for long responses.
        """
        try:
            await self.bot.send_chat_action(
                chat_id=user_id,
                action=ChatAction.TYPING
            )
        except Exception as e:
            logger.warning(f"Typing indicator failed: {e}")

    async def send_message(self, user_id: str, text: str) -> None:
        """Send final response to user."""
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=text
            )
        except Exception as e:
            logger.error(f"Send message failed: {e}")
            raise

    async def stream_message(self, user_id: str, chunks: AsyncIterator[str]) -> None:
        """
        Stream response to Telegram.
        Strategy: send placeholder → edit as chunks arrive → final edit.
        This gives ChatGPT-like feel on Telegram.
        """
        try:
            # Step 1 — send placeholder
            sent = await self.bot.send_message(
                chat_id=user_id,
                text="..."
            )

            # Step 2 — accumulate and edit
            full_text = ""
            async for chunk in chunks:
                full_text += chunk
                # edit every 10 chars to avoid rate limiting
                if len(full_text) % 10 == 0:
                    try:
                        await self.bot.edit_message_text(
                            chat_id=user_id,
                            message_id=sent.message_id,
                            text=full_text
                        )
                    except Exception:
                        pass

            # Step 3 — final edit with complete response
            await self.bot.edit_message_text(
                chat_id=user_id,
                message_id=sent.message_id,
                text=full_text
            )

        except Exception as e:
            logger.error(f"Stream message failed: {e}")
            raise