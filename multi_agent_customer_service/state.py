"""
Bu dosyada Multi-Agent sisteminin ortak LangGraph State yapısı tanımlanır.
"""

from typing_extensions import NotRequired
from langgraph.graph import MessagesState


class CustomerServiceState(MessagesState):
    route: NotRequired[str]
    last_agent: NotRequired[str]