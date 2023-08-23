from typing import List

from DocumentationQualityAnalysis.analyze_library.models.doc_page import DocPage


def get_documentation_examples(doc_page: DocPage) -> List:
    page = doc_page.url
    soup = doc_page.content
    raw_examples = soup.find_all("pre")
    doc_examples = []

    for raw_example in raw_examples:
        example = raw_example.get_text()
        if "(" in example:
            doc_examples.append([example, page])

    return doc_examples



