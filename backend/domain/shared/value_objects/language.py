from dataclasses import dataclass
from enum import Enum


@dataclass
class Language(Enum):
    """Value object for language"""
    ENGLISH = "English"
    SWEDISH = "Svenska"