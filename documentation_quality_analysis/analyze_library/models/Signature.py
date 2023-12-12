from typing import List

from analyze_library.models.parameter import Parameter


class Signature:
    def __init__(self, name: str, parent: str = None, req_params: List[Parameter] = [], optional_params: List[Parameter] = [],
                 raw_text: str = "", source: str = ""):
        self.name = name
        self.parent = parent
        self.fully_qualified_name = self.parent + "." + self.name if self.parent else self.name
        self.req_params = req_params
        self.optional_params = optional_params
        self.raw_text = raw_text
        self.source = source
