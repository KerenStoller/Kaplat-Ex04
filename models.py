from enum import Enum

from pydantic import BaseModel


class CalculatorRequestBody(BaseModel):
    arguments: list[int]
    operation: str

class StackRequestBody(BaseModel):
    arguments: list[int]

class Action(BaseModel):
    flavor: str
    operation: str
    arguments: list[int]
    result: int