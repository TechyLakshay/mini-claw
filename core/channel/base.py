from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseChannel(ABC):
    """
    Abstract base class for all channel adapters.
    Every new channel (Slack, Discord, WhatsApp) must implement these methods.
    """

    @abstractmethod
    async def send_typing(self, user_id: str) -> None:
        """Show typing indicator to user."""
        ...

    @abstractmethod
    async def send_message(self, user_id: str, text: str) -> None:
        """Send a plain text message to user."""
        ...

    @abstractmethod
    async def stream_message(self, user_id: str, chunks: AsyncIterator[str]) -> None:
        """Stream response chunks to user."""
        ...