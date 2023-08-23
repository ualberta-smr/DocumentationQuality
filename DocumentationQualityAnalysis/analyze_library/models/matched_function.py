from DocumentationQualityAnalysis.analyze_library.models.method_signature import MethodSignature


class MatchedFunction:
    def __init__(self, method: MethodSignature, raw_example: str, original_call: str, url: str):
        self.method = method
        self.original_call = original_call
        self.raw_example = raw_example
        self.url = url
