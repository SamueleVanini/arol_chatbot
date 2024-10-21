from enum import Enum, auto
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_redis import RedisChatMessageHistory
import core.config


# Enum for chat history types
class MemoryType(Enum):
    NONE = auto()
    LOCAL = auto()
    REDIS = auto()


# Factory class for creating chat history objects
class ChatHistoryFactory:
    # Store for local chat histories (for in-memory sessions)
    store = {}

    def __init__(self) -> None:
        raise EnvironmentError(
            "ChatHistoryFactory is designed to be instantiated using"
            "the `get_chat_history(cls, session_id: str, history_type: HistoryType)` method."
        )

    @classmethod
    def get_chat_history(cls, memory_type: MemoryType):
        """
        Factory method to return the appropriate chat history based on the history type (local or redis).
        """
        match memory_type:
            case MemoryType.LOCAL:
                return cls._get_local_session_history
            case MemoryType.REDIS:
                return cls._get_redis_history
            case _:
                raise ValueError(f"Unsupported history type: {memory_type}")

    def _get_local_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Return a local (in-memory) chat message history for a session."""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    @staticmethod
    def _get_redis_history(session_id: str) -> BaseChatMessageHistory:
        """Return a Redis-based chat message history for a session."""
        return RedisChatMessageHistory(session_id=session_id, redis_url=core.config.REDIS_URL)
