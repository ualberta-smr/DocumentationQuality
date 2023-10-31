from analyze_library.models.Signature import Signature
from analyze_library.models.doc_code_example import DocCodeExample


class MatchedCall:
    def __init__(self, called_signature: Signature, raw_example: DocCodeExample, original_call: str, url: str):
        self.called_signature: Signature = called_signature
        self.raw_example: DocCodeExample = raw_example
        self.original_call: str = original_call
        self.url = url
