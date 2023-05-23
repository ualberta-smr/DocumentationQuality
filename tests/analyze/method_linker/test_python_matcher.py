from unittest import TestCase
from unittest.mock import Mock

from Summary.analyze.MethodLinker import python_matcher


class TestPythonMatcher(TestCase):
    def test_get_declared_variable_mapping__with_example_of__import_and_assignment_variable(self):
        mock_example_code = "import pandas as pd\n" \
                            "df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "df.describe()"
        mock_classes = {'Series': "class info", "DataFrame": "class info"}
        declared_variable_mapping = python_matcher.get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of__jn_prefix_in_code_examples(self):
        mock_example_code = "In [1]: import pandas as pd\n" \
                            "In [2]:df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            "In[3]:df.describe()\n" \
                            "Out [3]:"

        mock_classes = {'Series': "class info", "DataFrame": "class info"}
        declared_variable_mapping = python_matcher.get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_get_declared_variable_mapping__with_example_of___prefix_in_code_examples(self):
        mock_example_code = ">>> import pandas as pd\n" \
                            ">>>df = pd.DataFrame({'A': [1, 2, 3]})\n" \
                            ">>> df.describe()\n" \
                            ">>>"

        mock_classes = {'Series': "class info", "DataFrame": "class info"}
        declared_variable_mapping = python_matcher.get_declared_variable_mapping(mock_example_code, mock_classes)

        expected_declared_variable_mapping = {"df": "DataFrame", "pd": "pandas"}

        self.assertEqual(declared_variable_mapping, expected_declared_variable_mapping)

    def test_match_call_with_other_class_functions(self):
        mock_module = Mock()
        mock_call = 'pd.method1'
        mock_classes = {'pandas': 'class1',
                        'DataFrame': 'class2',
                        'numpy': 'class3'}
        mock_functions = {'x.method1': 'x_function1',
                          'pandas.method1': 'pandas_function1',
                          'pandas.method2': 'pandas_function2',
                          'pandas.method3': 'pandas_function3',
                          'DataFrame.method1': 'df_function1',
                          'DataFrame.method2': 'df_function2'}
        mock_var_declarations = {'pd': 'pandas'}
        method1_func_object = Mock()
        method1_func_object.__qualname__ = 'pandas.method1'
        method1_func_object.__module__ = 'module1'
        mock_class_members = [('method1', method1_func_object), ('method2', Mock()), ('method3', Mock())]
        python_matcher.inspect.getmembers = Mock(return_value=mock_class_members)

        matched_function = python_matcher.match_call_with_other_class_functions(mock_module, mock_classes,
                                                                                mock_functions, mock_call,
                                                                                mock_var_declarations)

        expected_matched_function = 'pandas_function1'

        self.assertEqual(matched_function, expected_matched_function)

    def test_match_call_with_other_class_functions__returns_none__when_no_match(self):
        mock_module = Mock()
        mock_call = 'df.method1'
        mock_classes = {'pandas': 'class1',
                        'DataFrame': 'class2',
                        'numpy': 'class3'}
        mock_functions = {'x.method1': 'x_function1',
                          'pandas.method1': 'pandas_function1',
                          'pandas.method2': 'pandas_function2',
                          'pandas.method3': 'pandas_function3',
                          'DataFrame.method1': 'df_function1',
                          'DataFrame.method2': 'df_function2'}
        mock_var_declarations = {'pd': 'pandas'}
        method1_func_object = Mock()
        method1_func_object.__qualname__ = 'pandas.method1'
        method1_func_object.__module__ = 'module1'
        mock_class_members = [('method1', method1_func_object), ('method2', Mock()), ('method3', Mock())]
        python_matcher.inspect.getmembers = Mock(return_value=mock_class_members)

        matched_function = python_matcher.match_call_with_other_class_functions(mock_module, mock_classes,
                                                                                mock_functions, mock_call,
                                                                                mock_var_declarations)

        expected_matched_function = None

        self.assertEqual(matched_function, expected_matched_function)

    def test_match_call_with_other_class_functions__returns_function__when__module_matched(self):
        mock_module = Mock()
        mock_call = 'pd.date_range'
        mock_classes = {'pandas': 'class1',
                        'DataFrame': 'class2',
                        'numpy': 'class3'}
        mock_functions = {'indexes.date_range': 'indexes_function1',
                          'pandas.method1': 'pandas_function1',
                          'pandas.method2': 'pandas_function2',
                          'DataFrame.method1': 'df_function1',
                          'DataFrame.method2': 'df_function2'}
        mock_var_declarations = {'pd': 'pandas'}
        method1_func_object = Mock()
        method1_func_object.__qualname__ = 'date_range'
        method1_func_object.__module__ = 'pandas.core.indexes.datetime'
        mock_class_members = [('date_range', method1_func_object), ('method2', Mock()), ]
        python_matcher.inspect.getmembers = Mock(return_value=mock_class_members)

        matched_function = python_matcher.match_call_with_other_class_functions(mock_module, mock_classes,
                                                                                mock_functions, mock_call,
                                                                                mock_var_declarations)

        expected_matched_function = 'indexes_function1'

        self.assertEqual(matched_function, expected_matched_function)
