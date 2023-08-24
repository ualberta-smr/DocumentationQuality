from DocumentationQualityAnalysis.analyze_library.models.doc_code_example import DocCodeExample
from DocumentationQualityAnalysis.analyze_library.models.method_signature import MethodSignature


class MatchedFunction:
    def __init__(self, method: MethodSignature, raw_example: DocCodeExample, original_call: str, url: str):
        self.method: MethodSignature = method
        self.raw_example: DocCodeExample = raw_example
        self.original_call: str = original_call
        self.url = url
