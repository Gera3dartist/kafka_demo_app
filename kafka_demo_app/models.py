from pydantic import BaseModel
from typing import List
from enum import Enum

class AnimalType(str, Enum):
    cat = "cat"
    dog = "dog"

class AnimalVote(BaseModel):
    choice: AnimalType
