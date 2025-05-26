import re

from pydantic import BaseModel, Field, field_validator
from pylatexenc.latexencode import unicode_to_latex

from writer import Writer


class Melody(BaseModel):
    """
    Musical melody for topic.
    """

    topic: str = Field(
        description="The topic for this melody.",
    )

    melody: str = Field(
        description="The melody in MusicTeX notation.",
    )

    explanation: str = Field(
        description="Detailed explanation describing how melody relates to the topic and the emotional journey it represents. "
        "Between 150-300 characters.",
        min_length=150,
        max_length=350,
    )

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z\s]+$", v.strip()):
            raise ValueError("Topic must contain only letters and spaces")
        return unicode_to_latex(v.title().strip())

    @field_validator("explanation")
    @classmethod
    def validate_explanation(cls, v: str) -> str:
        return unicode_to_latex(v.strip())

    def __str__(self):
        """
        Render in LaTeX with proper MusicTeX formatting.
        """

        return f"""
        \\melody{{{self.topic}}}{{
        \\begin{{music}}
        \\parindent10mm
        \\instrumentnumber{{1}}
        {self.melody}
        \\end{{music}}
        }}{{{self.explanation}}}
        """


writer = Writer(
    cls=Melody,
    prompt=r"""
        For the topic provided, create a musical melody with 4-12 notes that captures the emotional essence 
        of the topic. Topics are in the context of the human experience. Create the melody in MusicTeX notation.
        Write a explanation of how the melody relates to the topic, The explanation should be poetic yet informative. Explanation should be 150-300 characters.
        Make the melody rich, unique and profound; AVOID clichés (e.g. journeys, simple arcs) or overly simplistic patterns. Be
        creative and original!
        
        Use this MusicTeX notation for the melody:
        
        a = a3
        b = b3
        c = c4
        d = d4
        e = e4
        f = f4
        g = g4
        h = a4
        i = b4
        j = c5
        k = d5
        l = e5
        m = f5
        n = g5
        
        For sharps and flats, prefix the note with a sharp (^) or flat (_) symbol:
        e.g. ^c is C# (C sharp), _d is D flat (D♭).

        Example:
        Topic: "Childhood"
        
        Melody:
        \setstaffs1{1}
        \generalmeter{\meterfrac34}
        \generalsignature{2}
        \startextract
        \Notes\zq{c}\zq{e}\qu{g}\en % chord example
        \Notes\hu{m}\en % f5
        \Notes\qu{}\en % quarter note rest
        \Notes\qu{e}\qu{f}\qu{g}\en
        \Notes\wh{c}\en
        \endextract
        
        Explanation:
        This melody captures childhood nostalgia, rising from C through bright major tones (E, G), descending reflectively to D, then climbing again like a recalled memory before returning to C's gentle resolution.
""",
)
