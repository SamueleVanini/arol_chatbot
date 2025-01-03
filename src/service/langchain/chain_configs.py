from enum import Enum, auto


class ChainType(Enum):
    CHAT = auto()
    QA = auto()
    RETRIEVER = auto()
