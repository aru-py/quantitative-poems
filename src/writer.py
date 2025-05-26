"""
writer.py
"""

import logging

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt

from config import model_config


class Writer:
    """
    Base class for writers.
    """

    def __init__(self, cls, prompt):
        model = init_chat_model(**model_config)
        self.model = model.bind_tools([cls])
        self.cls = cls
        self.prompt = prompt

    def write(self, topic: str) -> str:
        """
        Writes a page.
        """
        return str(self.draft(topic=topic))

    @retry(stop=stop_after_attempt(3), after=logging.warning)
    def draft(self, topic: str):
        """
        Draft a page.
        """

        messages = [
            SystemMessage(self.prompt),
            HumanMessage(topic),
        ]

        res = self.model.invoke(messages)
        args = res.tool_calls[0]["args"]
        args["Topic"] = topic
        return self.cls(**args)
