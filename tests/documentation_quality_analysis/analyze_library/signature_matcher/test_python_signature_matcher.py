from typing import List
from unittest import TestCase

from documentation_quality_analysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from documentation_quality_analysis.analyze_library.models.doc_code_example import DocCodeExample
from documentation_quality_analysis.analyze_library.models.method_signature import MethodSignature
from documentation_quality_analysis.analyze_library.signature_matcher.python_doc_api_to_example_signature_matcher import \
    match_examples_to_doc_api, _get_declared_variable_mapping


class TestPythonSignatureMatcher(TestCase):
    def test_python_match_examples_1(self):
        mock_doc_api = [
            ClassConstructorSignature(name="DataFrame", parent="pandas",
                                      raw_text="class pandas.DataFrame(data=None, "
                                               "index=None, columns=None, dtype=None, copy=None)")]
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="import pandas as pd\n"
                                                                         "pd.DataFrame({'A': [1, 2, 3]})",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual("pandas.DataFrame", matched[0].called_signature.fully_qualified_name)
        self.assertEqual(1, len(matched))

    def test_python_match_examples_2(self):
        mock_doc_api = [
            MethodSignature(name="get", parent="requests.request",
                            raw_text="requests.request(method, url, **kwargs)"),
            MethodSignature(name="get", parent="requests.Session",
                            raw_text="requests.request(method, url, **kwargs)"),
            ClassConstructorSignature(name="Session", parent="requests", raw_text="requests.Session()")]
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="s = requests.Session()\n"
                                                                         "s.get()",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual("requests.Session", matched[0].called_signature.fully_qualified_name)
        self.assertEqual("requests.Session.get", matched[1].called_signature.fully_qualified_name)
        self.assertEqual(2, len(matched))

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
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="from requests import Request, Session\n"
                                                                         "s = Session()\n"
                                                                         "req = Request('POST', url, data=data, headers=headers)\n"
                                                                         "prepped = req.prepare()\n"
                                                                         "s.get(‘https://smth.org/get’)",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual("requests.Session", matched[0].called_signature.fully_qualified_name)
        self.assertEqual("requests.Request", matched[1].called_signature.fully_qualified_name)
        self.assertEqual("requests.Request.prepare", matched[2].called_signature.fully_qualified_name)
        self.assertEqual("requests.Session.get", matched[3].called_signature.fully_qualified_name)
        self.assertEqual(4, len(matched))

    def test_python_match_examples_where_api_should_not_match_1(self):
        mock_doc_api = [
            ClassConstructorSignature(name="Series", parent="pandas"),
            MethodSignature(name="hist", parent="Series.plot",
                            raw_text="Series.plot.hist()")
        ]
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="df=pd.DataFrame()\n"
                                                                         "ax = df.plot.hist(bins=12, alpha=0.5)",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual([], matched)

    def test_python_match_examples_where_api_should_not_match_2(self):
        mock_doc_api = [
            MethodSignature(name="hist", parent="Series.plot",
                            raw_text="Series.plot.hist()"),
            MethodSignature(name="hist", parent="DataFrame.plot",
                            raw_text="DataFrame.plot.hist()")
        ]
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="df=pd.DataFrame()\n"
                                                                         "ax = df.plot.hist(bins=12, alpha=0.5)",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual([], matched)

    def test_python_match_examples_where_api_should_match_4(self):
        mock_doc_api = [
            ClassConstructorSignature(name="Series", parent="pandas"),
            ClassConstructorSignature(name="DataFrame", parent="pandas"),
            MethodSignature(name="hist", parent="Series.plot",
                            raw_text="Series.plot.hist()"),
            MethodSignature(name="hist", parent="DataFrame.plot",
                            raw_text="DataFrame.plot.hist()")
        ]
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="df=pd.DataFrame()\n"
                                                                         "ax = df.plot.hist(bins=12, alpha=0.5)",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual("pandas.DataFrame", matched[0].called_signature.fully_qualified_name)
        self.assertEqual("DataFrame.plot.hist", matched[1].called_signature.fully_qualified_name)
        self.assertEqual(2, len(matched))

    def test_python_match_examples_where_api_should_match_5(self):
        mock_doc_api = [
            ClassConstructorSignature(name="Series", parent="pandas"),
            MethodSignature(name="sort_values", parent="Series",
                            raw_text="Series.sort_values()"),
            MethodSignature(name="lower", parent="Series.str",
                            raw_text="Series.str.lower()")
        ]
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="s = pd.Series()\n"
                                                                         "s.sort_values(key=lambda x: x.str.lower())",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual("pandas.Series", matched[0].called_signature.fully_qualified_name)
        self.assertEqual("Series.sort_values", matched[1].called_signature.fully_qualified_name)
        self.assertEqual(2, len(matched))

    def test_python_match_examples_where_api_should_match_6(self):
        mock_doc_api = [
            ClassConstructorSignature(name="Series", parent="pandas"),
            MethodSignature(name="round", parent="Series.dt",
                            raw_text="Series.dt.round()"),
            MethodSignature(name="all", parent="Series",
                            raw_text="Series.all()")
        ]
        matched = match_examples_to_doc_api("",
                                            examples=[DocCodeExample(example="pd.Series(rng).dt.round('H')\n"
                                                                         "pd.Series([True, True]).all()",
                                                                 url="some_url")],
                                            doc_apis=mock_doc_api)

        self.assertEqual("pandas.Series", matched[0].called_signature.fully_qualified_name)
        self.assertEqual("Series.dt.round", matched[1].called_signature.fully_qualified_name)
        self.assertEqual("Series.all", matched[2].called_signature.fully_qualified_name)
        self.assertEqual(3, len(matched))

    def test_python_match_examples_where_api_should_match_7(self):
        mock_doc_api = [
            ClassConstructorSignature(name="Series", parent="pandas"),
            MethodSignature(name="normalize", parent="pandas.Series.str",
                            raw_text="Series.str.normalize()"),
        ]
        matched = match_examples_to_doc_api("", examples=[
            DocCodeExample(example="ser = pd.Series(['ñ'])\n"
                                   "ser.str.normalize('NFC') == ser.str.normalize('NFD')",
                           url="some_url")], doc_apis=mock_doc_api)

        self.assertEqual("pandas.Series", matched[0].called_signature.fully_qualified_name)
        self.assertEqual("pandas.Series.str.normalize", matched[1].called_signature.fully_qualified_name)
        self.assertEqual(2, len(matched))

    def test_python_match_examples_where_api_should_not_match_with_multiple_same_named_method(self):
        mock_doc_api = [
            ClassConstructorSignature(name="Series", parent="pandas"),
            ClassConstructorSignature(name="DataFrame", parent="pandas"),
            MethodSignature(name="hist", parent="pandas.Series",
                            raw_text="Series.hist"),
            MethodSignature(name="hist", parent="pandas.DataFrame",
                            raw_text="DataFrame.hist")
        ]
        matched = match_examples_to_doc_api("", examples=[
            DocCodeExample(example="hist()",
                           url="some_url")], doc_apis=mock_doc_api)

        self.assertEqual([], matched)

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
        declared_variable_mapping = _get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"s": "Session"}

        self.assertEqual(expected_declared_variable_mapping, declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example__class_name_variable_assignment(self):
        mock_example_code = "from requests import Request, Session\n" \
                            "s = Session()\n" \
                            "req = Request('POST', url, data=data, headers=headers)\n" \
                            "prepped = req.prepare()\n" \
                            "s.get(‘https://smth.org/get’)"
        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Session", parent="requests"),
                                                         ClassConstructorSignature(name="Request", parent="requests")]
        declared_variable_mapping = _get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"s": "Session",
                                              "req": "Request"}

        self.assertEqual(expected_declared_variable_mapping, declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of__import_and_assignment_variable(self):
        mock_example_code = "import pandas as pd\n" \
                            "df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "df.describe()"
        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Series", parent="pandas"),
                                                         ClassConstructorSignature(name="DataFrame", parent="pandas")]
        declared_variable_mapping = _get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(expected_declared_variable_mapping, declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of__jn_prefix_in_code_examples(self):
        mock_example_code = "In [1]: import pandas as pd\n" \
                            "In [2]:df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "In[3]:df.describe()\n" \
                            "Out [3]:"

        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Series", parent="pandas"),
                                                         ClassConstructorSignature(name="DataFrame", parent="pandas")]
        declared_variable_mapping = _get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(expected_declared_variable_mapping, declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of___prefix_in_code_examples(self):
        mock_example_code = ">>> import pandas as pd\n" \
                            ">>>df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            ">>> df.describe()\n" \
                            ">>>"
        mock_class_1 = ClassConstructorSignature(name="Series", parent="pandas")
        mock_class_2 = ClassConstructorSignature(name="DataFrame", parent="pandas")

        mock_classes: List[ClassConstructorSignature] = [mock_class_1, mock_class_2]
        declared_variable_mapping = _get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(expected_declared_variable_mapping, declared_variable_mapping)
