from typing import List
from unittest import TestCase

from DocumentationQualityAnalysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from DocumentationQualityAnalysis.analyze_library.models.doc_code_example import DocCodeExample
from DocumentationQualityAnalysis.analyze_library.signature_matcher.python_signature_matcher import \
    python_match_examples, get_declared_variable_mapping


class TestPythonSignatureMatcher(TestCase):
    def test_python_match_examples(self):
        mock_doc_api = [
            ClassConstructorSignature(name="DataFrame", parent="pandas",
                                      raw_text="class pandas.DataFrame(data=None, "
                                               "index=None, columns=None, dtype=None, copy=None)")]
        matched = python_match_examples("",
                                        examples=[DocCodeExample(example="import pandas as pd\n"
                                                                         "pd.DataFrame({'A': [1, 2, 3]})",
                                                                 url="some_url")],
                                        doc_apis=mock_doc_api)

        self.assertTrue(matched[0].method.fully_qualified_name, "pandas.DataFrame")

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

        mock_classes: List[ClassConstructorSignature] = [ClassConstructorSignature(name="Series", parent="pandas"),
                                                         ClassConstructorSignature(name="DataFrame", parent="pandas")]
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)
