from typing import List

from DocumentationQualityAnalysis.analyze_library.models.Signature import Signature
from DocumentationQualityAnalysis.analyze_library.models.parameter import Parameter


class MethodSignature(Signature):
    def __init__(self, name: str, parent: str, req_params: List[Parameter] = [], optional_params: List[Parameter] = [],
                 return_type: str = None, raw_text: str = ''):
        super().__init__(name, parent, req_params, optional_params, raw_text)

        self.fully_qualified_name = self.parent + "." + self.name if self.parent else self.name
        self.return_type = return_type
