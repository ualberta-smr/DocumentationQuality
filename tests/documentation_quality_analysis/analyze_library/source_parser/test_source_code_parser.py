from unittest import TestCase

from documentation_quality_analysis.analyze_library.source_parser.source_code_parser import _get_python_signatures


class Test(TestCase):
    def test__get_python_signatures(self):
        mapped_signatures = {}
        signatures = _get_python_signatures('./test_src_python_file.py', mapped_signatures)

        keys = list(mapped_signatures.keys())
        self.assertEqual(5, len(signatures))
        self.assertEqual(mapped_signatures[keys[0]][0].fully_qualified_name, 'Class1_NDFrame')
        self.assertEqual(mapped_signatures[keys[1]][0].fully_qualified_name, 'class_2_Series')
        self.assertEqual(mapped_signatures[keys[2]][0].fully_qualified_name, 'class_2_Series.func1_in_series')
        self.assertEqual(mapped_signatures[keys[3]][0].fully_qualified_name, 'class_2_Series.func2_in_series')
        self.assertEqual(mapped_signatures[keys[4]][0].fully_qualified_name, 'test_src_python_file.py.func2_ravel')
