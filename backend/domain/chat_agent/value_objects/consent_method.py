from dataclasses import dataclass
from enum import Enum


@dataclass
class ConsentMethod(Enum):
    """Consent method"""
    TYPED = "typed"
    VOICE = "voice"
    SIGNATURE = "signature"
    TYPED_AND_SIGNATURE = "typed+signature"
