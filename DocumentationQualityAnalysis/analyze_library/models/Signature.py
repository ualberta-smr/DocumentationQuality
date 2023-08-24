from typing import List

from DocumentationQualityAnalysis.analyze_library.models.parameter import Parameter


class Signature:
    def __init__(self, name: str, parent: str, req_params: List[Parameter] = [], optional_params: List[Parameter] = [],
                 raw_text: str = ""):
        self.name = name
        self.parent = parent
        self.req_params = req_params
        self.optional_params = optional_params
        self.raw_text = raw_text
