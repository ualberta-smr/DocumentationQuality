from enum import Enum


class PromptMode(Enum):
    FEW_SHOT = "few-shot"
    ONE_SHOT = "one-shot"
    ZERO_SHOT = "zero-shot"
    CHAIN_OF_THOUGHT = "chain-of-thought"

