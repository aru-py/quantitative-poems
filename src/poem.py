import re
from typing import List

from pydantic import BaseModel, Field, field_validator
from pylatexenc.latexencode import unicode_to_latex


class Variable(BaseModel):
    """Individual variable used in the equation."""

    symbol: str = Field(
        description="Mathematical symbol for the variable in LaTeX format (e.g., 'x', 'v_0', '\\alpha')"
    )

    name: str = Field(
        description="Clear, concise variable name (1 word, letters only)",
        min_length=3,
        max_length=15
    )
    description: str = Field(
        description="Explanation of the variable's role, meaning, and relationship to other variables in the equation context",
        min_length=140,
        max_length=220
    )

    @classmethod
    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        if not re.match(r'^[A-Za-z\s]+$', v.strip()):
            raise ValueError('Name must contain only letters and spaces')
        return unicode_to_latex(v.title().strip())

    @classmethod
    @field_validator('symbol')
    def validate_description(cls, v: str) -> str:
        return unicode_to_latex(v.strip())

    def __str__(self):
        """
        Render in LaTeX.
        """
        return r"\item $%s$: \index{%s}\textit{%s}. %s" % (self.symbol, self.name, self.name, self.description)


class Poem(BaseModel):
    """
    Model for creating a mathematical equation with comprehensive variable definitions.
    Designed for educational and analytical purposes.
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
        max_length=8
    )
    explanation: str = Field(
        description="Detailed mathematical explanation describing how the variables interact, the equation's significance, and its practical applications"
    )

    @classmethod
    @field_validator('equation')
    def validate_equation(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Equation cannot be empty')
        return v.strip()

    @classmethod
    @field_validator('variables')
    def validate_unique_symbols(cls, v: List[Variable]) -> List[Variable]:
        symbols = [var.symbol for var in v]
        if len(symbols) != len(set(symbols)):
            raise ValueError('All variable symbols must be unique')
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
                        "description": "The net external force applied to an object, measured in Newtons, which causes acceleration proportional to the object's mass and inversely affects motion."
                    }
                ],
                "explanation": "This fundamental equation describes the relationship between force, mass, and acceleration in classical mechanics."
            }
        }

    def __str__(self):
        """
        Render in LaTeX.
        """
        equation = re.sub(r".*=", f"{self.topic} =", self.equation)
        variables = [str(variable) for variable in self.variables[1:]]
        return r"\poem{%s}{%s}{%s}{%s}" % (self.topic, equation, "\n".join(variables), self.explanation)
