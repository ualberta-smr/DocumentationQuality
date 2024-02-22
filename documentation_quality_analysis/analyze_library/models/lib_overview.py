from pydantic import BaseModel


class LibraryOverview(BaseModel):
    library_name: str
    description: str
    gh_url: str
    doc_url: str
    language: str
    methods_with_code_examples_ratio: float | int
    classes_with_code_examples_ratio: float | int
    documented_methods: int
    documented_classes: int
    doc_api_consistency_ratio: float | int
    matched_doc_api_len: float | int
    unmatched_doc_api_len: float | int
    unmatched_doc_api: str
    text_readability_score: float | int
    navigability_score: float | int
    general_rating: float | int
    task_list_done: bool




