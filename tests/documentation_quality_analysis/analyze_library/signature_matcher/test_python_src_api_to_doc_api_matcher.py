from unittest import TestCase

from documentation_quality_analysis.analyze_library.models.Signature import Signature
from documentation_quality_analysis.analyze_library.signature_matcher.python_src_api_to_doc_api_matcher import \
    match_doc_api_to_src_api


class Test(TestCase):
    def test_match_doc_api_to_src_api(self):
        mock_mapped_src_api = {'close': [Signature(
            name='close',
            parent='Session'
        )]}

        mock_doc_api = [Signature(name='close', parent='requests.Session')]

        match, not_match = match_doc_api_to_src_api(doc_apis=mock_doc_api, mapped_src_apis=mock_mapped_src_api)

        self.assertEqual(match == [])
