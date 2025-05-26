import logging

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt

from config import model_config
from poem import Poem
from utils import Writer


class PoemWriter(Writer):
    """
    Writes a page.
    """

    def __init__(self):
        model = init_chat_model(**model_config)
        model = model.bind_tools([Poem])
        super().__init__(model=model)

    def write(self, topic: str) -> str:
        """
        Writes a page.
        """
        return str(self.draft(topic=topic))

    @retry(stop=stop_after_attempt(3), after=logging.warning)
    def draft(self, topic: str) -> Poem:
        """
        Draft a page.
        """

        write_prompt = r"""
        For the topic provided, create an equation with 4-5 variables and use the
        full gamut of mathematics to express it (e.g. exponents, calculus, logs, trignometry). Choose 1-2 of 
        the prior. The equation should be profound. Have a pedagogical tone. Topics are in the context of human life. Write out a detailed, poetic 
        explanation for the equation and how the variables relate. Write equation in Latex. Each variable
        description should be between 50 - 150 characters. Explanation should be 200 - 300 characters.

        Here is an example:
        Equation: C = \frac{K_i^n}{D + E}

        Variables:
        - $C$: *Curiosity*. A strong desire to know or learn something.
        - $K_i$: *Knowledge*. Represents the rate at which an individual is able to absorb and make sense of new information, which is why it's on the top.
        - $D$: *Distractions*. Sum of external factors that divert attention away from focusing on learning or exploring, which is why it's on the bottom of the fraction.
        - $E$: *Experience*. The accumulated knowledge or mastery over a subject, which could both enhance and deter curiosity through familiarity.

        Explanation:
        This equation captures love as the product of positive emotional forces divided by protective barriers. Affection, empathy, and time investment multiply to create strong bonds, while vulnerability and fear act as denominators that can limit love's full expression. The mathematical relationship shows that as we overcome our fears and allow ourselves to be vulnerable, love grows exponentially through genuine care and shared time.
        """

        messages = [
            SystemMessage(write_prompt),
            HumanMessage(topic),
        ]

        res = self.model.invoke(messages)
        args = res.tool_calls[0]['args']
        args['Topic'] = topic
        return Poem(**args)
