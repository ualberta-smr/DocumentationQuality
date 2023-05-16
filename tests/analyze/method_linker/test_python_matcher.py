from unittest import TestCase

from Summary.analyze.MethodLinker.python_matcher import get_declared_variable_mapping


class TestPythonMatcher(TestCase):
    def test_get_declared_variable_mapping__with_example_of__import_and_assignment_variable(self):
        mock_example_code = "import pandas as pd\n" \
                            "df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "df.describe()"
        mock_classes = {'Series': "class info", "DataFrame": "class info"}
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of__jn_prefix_in_code_examples(self):
        mock_example_code = "In [1]: import pandas as pd\n" \
                            "In [2]:df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "In[3]:df.describe()\n" \
                            "Out [3]:"

        mock_classes = {'Series': "class info", "DataFrame": "class info"}
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of___prefix_in_code_examples(self):
        mock_example_code = ">>> import pandas as pd\n" \
                            ">>>df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            ">>> df.describe()\n" \
                            ">>>"

        mock_classes = {'Series': "class info", "DataFrame": "class info"}
        declared_variable_mapping = get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)
