from typing import List

from analyze_library.models.Signature import Signature
from analyze_library.models.parameter import Parameter


class MethodSignature(Signature):
    def __init__(self, name: str, parent: str | None, req_params: List[Parameter] = [],
                 optional_params: List[Parameter] = [],
                 return_type: str = None, raw_text: str = '', source: str = ""):
        super().__init__(name, parent, req_params, optional_params, raw_text, source)

        self.return_type = return_type
