from unittest import TestCase
from bs4 import BeautifulSoup

from DocumentationQualityAnalysis.analyze_library.doc_parser.doc_parser import \
    get_functions_and_classes_from_doc_api_ref
from DocumentationQualityAnalysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from DocumentationQualityAnalysis.analyze_library.models.doc_page import DocPage
from DocumentationQualityAnalysis.analyze_library.models.method_signature import MethodSignature


class TestDocParser(TestCase):
    with open("./test.html", "r") as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    def test_get_functions_and_classes_from_doc_api_ref(self):
        doc_pages = [DocPage(url="https://some_url/api", content=self.soup)]
        doc_apis = get_functions_and_classes_from_doc_api_ref(doc_pages)
        len_of_func = [x for x in doc_apis if type(x) == MethodSignature]
        len_of_classes = [x for x in doc_apis if type(x) == ClassConstructorSignature]

        self.assertTrue(len(doc_apis), 28)
        self.assertTrue(len_of_func, 27)
        self.assertTrue(len_of_classes, 1)
