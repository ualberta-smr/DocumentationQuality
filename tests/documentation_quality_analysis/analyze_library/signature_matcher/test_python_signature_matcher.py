from typing import List
from unittest import TestCase

from documentation_quality_analysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from documentation_quality_analysis.analyze_library.models.doc_code_example import DocCodeExample
from documentation_quality_analysis.analyze_library.models.method_signature import MethodSignature
from documentation_quality_analysis.analyze_library.signature_matcher.python_signature_matcher import \
    python_match_examples, get_declared_variable_mapping


class TestPythonSignatureMatcher(TestCase):
    def test_python_match_examples_1(self):
        mock_doc_api = [
            ClassConstructorSignature(name="DataFrame", parent="pandas",
                                      raw_text="class pandas.DataFrame(data=None, "
                                               "index=None, columns=None, dtype=None, copy=None)")]
        matched = python_match_examples("",
                                        examples=[DocCodeExample(example="import pandas as pd\n"
                                                                         "pd.DataFrame({'A': [1, 2, 3]})",
                                                                 url="some_url")],
                                        doc_apis=mock_doc_api)

        self.assertEqual(matched[0].called_signature.fully_qualified_name, "pandas.DataFrame")

    def test_python_match_examples_2(self):
        mock_doc_api = [
            MethodSignature(name="get", parent="requests.request",
                            raw_text="requests.request(method, url, **kwargs)"),
            MethodSignature(name="get", parent="requests.Session",
                            raw_text="requests.request(method, url, **kwargs)"),
            ClassConstructorSignature(name="Session", parent="requests", raw_text="requests.Session()")]
        matched = python_match_examples("",
                                        examples=[DocCodeExample(example="s = requests.Session()\n"
                                                                         "s.get()",
                                                                 url="some_url")],
                                        doc_apis=mock_doc_api)

        self.assertEqual(matched[0].called_signature.fully_qualified_name, "requests.Session")
        self.assertEqual(matched[1].called_signature.fully_qualified_name, "requests.Session.get")

    def test_python_match_examples_3(self):
        mock_doc_api = [
            MethodSignature(name="get", parent="requests.request",
                            raw_text="requests.request(method, url, **kwargs)"),
            MethodSignature(name="prepare", parent="requests.Request",
                            raw_text="requests.Request.prepare()"),
            MethodSignature(name="get", parent="requests.Session",
                            raw_text="requests.request(method, url, **kwargs)"),
            ClassConstructorSignature(name="Session", parent="requests", raw_text="requests.Session()"),
            ClassConstructorSignature(name="Request", parent="requests", raw_text="requests.Request()")]
        matched = python_match_examples("",
                                        examples=[DocCodeExample(example="from requests import Request, Session\n"
                                                                         "s = Session()\n"
                                                                         "req = Request('POST', url, data=data, headers=headers)\n"
                                                                         "prepped = req.prepare()\n"
                                                                         "s.get(‘https://smth.org/get’)",
                                                                 url="some_url")],
                                        doc_apis=mock_doc_api)

        self.assertEqual(matched[0].called_signature.fully_qualified_name, "requests.Session")
        self.assertEqual(matched[1].called_signature.fully_qualified_name, "requests.Request")
        self.assertEqual(matched[2].called_signature.fully_qualified_name, "requests.Request.prepare")
        self.assertEqual(matched[3].called_signature.fully_qualified_name, "requests.Session.get")


    # def test_python_match_examples_4(self):
    #     mock_doc_api = [
    #         MethodSignature(name="get", parent="requests.request",
    #                         raw_text="requests.request(method, url, **kwargs)"),
    #         MethodSignature(name="get", parent="requests.Session",
    #                         raw_text="requests.request(method, url, **kwargs)"),
    #         ClassConstructorSignature(name="Session", parent="requests", raw_text="requests.Session()")]
    #     matched = python_match_examples("",
    #                                     examples=[DocCodeExample(example="with requests.Session() as s:\n"
    #                                                                      "s.get(‘https://smth.org/get’)",
    #                                                              url="some_url")],
    #                                     doc_apis=mock_doc_api)
    #
    #     self.assertEqual(matched[0].called_signature.fully_qualified_name, "requests.Session")
    #     self.assertEqual(matched[1].called_signature.fully_qualified_name, "requests.Session.get")

    def test_get_declared_variable_mapping__with_example__variable_assignment(self):
        mock_example_code = "s = requests.Session()\n" \
                            "s.get()"
        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Session", parent="requests"),
                                                         ClassConstructorSignature(name="Request", parent="requests")]
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"s": "Session"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example__class_name_variable_assignment(self):
        mock_example_code = "from requests import Request, Session\n" \
                            "s = Session()\n" \
                            "req = Request('POST', url, data=data, headers=headers)\n" \
                            "prepped = req.prepare()\n" \
                            "s.get(‘https://smth.org/get’)"
        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Session", parent="requests"),
                                                         ClassConstructorSignature(name="Request", parent="requests")]
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"s": "Session",
                                              "req": "Request"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of__import_and_assignment_variable(self):
        mock_example_code = "import pandas as pd\n" \
                            "df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "df.describe()"
        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Series", parent="pandas"),
                                                         ClassConstructorSignature(name="DataFrame", parent="pandas")]
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of__jn_prefix_in_code_examples(self):
        mock_example_code = "In [1]: import pandas as pd\n" \
                            "In [2]:df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "In[3]:df.describe()\n" \
                            "Out [3]:"

        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Series", parent="pandas"),
                                                         ClassConstructorSignature(name="DataFrame", parent="pandas")]
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of___prefix_in_code_examples(self):
        mock_example_code = ">>> import pandas as pd\n" \
                            ">>>df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            ">>> df.describe()\n" \
                            ">>>"
        mock_class_1 = ClassConstructorSignature(name="Series", parent="pandas")
        mock_class_2 = ClassConstructorSignature(name="DataFrame", parent="pandas")

        mock_classes: List[ClassConstructorSignature] = [mock_class_1, mock_class_2]
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)
