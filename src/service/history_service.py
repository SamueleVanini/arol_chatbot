from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_redis import RedisChatMessageHistory

import core.config

store = {}


def get_local_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id, redis_url=core.config.REDIS_URL)


def connect_history_session(session_id, is_local=False):
    if is_local:
        return get_local_session_history(session_id=session_id)
    else:
        return get_redis_history(session_id=session_id)
