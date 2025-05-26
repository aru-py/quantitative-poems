import re
from typing import List

from pydantic import BaseModel, Field, field_validator
from pylatexenc.latexencode import unicode_to_latex

from writer import Writer


class Variable(BaseModel):
    """
    Variable for mathematical poem.
    """

    symbol: str = Field(
        description="Mathematical symbol for the variable in LaTeX format (e.g., 'x', 'v_0', '\\alpha')"
    )

    name: str = Field(
        description="Clear, concise variable name (1 word, letters only)",
        min_length=3,
        max_length=15,
    )
    description: str = Field(
        description="Explanation of the variable's role, meaning, and relationship to other variables in the equation context",
        min_length=140,
        max_length=220,
    )

    @classmethod
    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z\s]+$", v.strip()):
            raise ValueError("Name must contain only letters and spaces")
        return unicode_to_latex(v.title().strip())

    @classmethod
    @field_validator("symbol")
    def validate_description(cls, v: str) -> str:
        return unicode_to_latex(v.strip())

    def __str__(self):
        """
        Render in LaTeX.
        """
        return r"\item $%s$: \index{%s}\textit{%s}. %s" % (
            self.symbol,
            self.name,
            self.name,
            self.description,
        )


class Poem(BaseModel):
    """
    Mathematical poem.
    """

    topic: str = Field(
        description="The topic for this equation.",
    )
    equation: str = Field(
        description="Complete equation in proper LaTeX format, ready for rendering",
    )
    variables: List[Variable] = Field(
        description="Comprehensive list of all variables appearing in the equation",
        min_length=4,
        max_length=8,
    )
    explanation: str = Field(
        description="Detailed mathematical explanation describing how the variables interact, the equation's significance, and its practical applications"
    )

    @classmethod
    @field_validator("equation")
    def validate_equation(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Equation cannot be empty")
        return v.strip()

    @classmethod
    @field_validator("variables")
    def validate_unique_symbols(cls, v: List[Variable]) -> List[Variable]:
        symbols = [var.symbol for var in v]
        if len(symbols) != len(set(symbols)):
            raise ValueError("All variable symbols must be unique")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Newton's Second Law",
                "equation": "F = ma",
                "variables": [
                    {
                        "symbol": "F",
                        "name": "Force",
                        "description": "The net external force applied to an object, measured in Newtons, which causes acceleration proportional to the object's mass and inversely affects motion.",
                    }
                ],
                "explanation": "This fundamental equation describes the relationship between force, mass, and acceleration in classical mechanics.",
            }
        }

    def __str__(self):
        """
        Render in LaTeX.
        """
        equation = re.sub(r".*=", f"{self.topic} =", self.equation)
        variables = [str(variable) for variable in self.variables[1:]]
        return r"\poem{%s}{%s}{%s}{%s}" % (
            self.topic,
            equation,
            "\n".join(variables),
            self.explanation,
        )


writer = Writer(
    cls=Poem,
    prompt=r"""
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
        """,
)
