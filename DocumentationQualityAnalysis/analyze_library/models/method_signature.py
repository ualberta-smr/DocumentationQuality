from typing import List

from DocumentationQualityAnalysis.analyze_library.models.parameter import Parameter


class MethodSignature:
    def __init__(self, name: str, parent: str, req_params: List[Parameter] = [], optional_params: List[Parameter] = [],
                 return_type: str = None, raw_text: str = ''):
        self.name = name
        self.parent = parent
        self.fully_qualified_name = self.parent + "." + self.name if self.parent else self.name
        self.req_params = req_params
        self.optional_params = optional_params
        self.return_type = return_type
        self.raw_text = raw_text
