from unittest import TestCase
from bs4 import BeautifulSoup

from documentation_quality_analysis.analyze_library.doc_parser.doc_parser import \
    get_functions_and_classes_from_doc_api_ref
from documentation_quality_analysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from documentation_quality_analysis.analyze_library.models.doc_page import DocPage
from documentation_quality_analysis.analyze_library.models.method_signature import MethodSignature


class TestDocParser(TestCase):
    with open("./test.html", "r") as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    def test_get_functions_and_classes_from_doc_api_ref(self):
        doc_pages = [DocPage(url="https://some_url/api", content=self.soup)]
        doc_apis = get_functions_and_classes_from_doc_api_ref(doc_pages)
        methods = [x.fully_qualified_name for x in doc_apis if type(x) == MethodSignature]
        classes = [x.fully_qualified_name for x in doc_apis if type(x) == ClassConstructorSignature]

        expected_methods = ['requests.request', 'requests.Session.close', 'requests.Session.send',
                            'pandas.Series.set_axis', 'pandas.Series.ffill', 'pandas.Series.spparam1',
                            'pandas.Series.spparam2']
        expected_classes = ['x.requests.Request', 'requests.Session', 'requests.RequestException']

        self.assertEqual(len(doc_apis), 9)
        self.assertEqual(len(methods), 7)
        self.assertEqual(len(classes), 3)
        self.assertEqual(expected_methods, methods)
        self.assertEqual(expected_classes, classes)
