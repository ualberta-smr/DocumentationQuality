from analyze_library.metric_calculation.navigability.navigability import get_navigability_score
from analyze_library.metric_calculation.text_readability.text_readability import get_text_readability


class Metrics:
    def __init__(self, doc_pages, example_per_method, example_per_class, matched_signatures, unmatched_signatures,
                 doc_url):
        self.methods_with_code_examples_ratio = self.get_api_with_code_example_ratio(example_per_method)
        self.classes_with_code_examples_ratio = self.get_api_with_code_example_ratio(example_per_class)
        self.consistency_ratio = self.get_consistency_ratio(matched_signatures, unmatched_signatures)
        self.text_readability_score = get_text_readability(doc_pages)
        self.navigability = get_navigability_score(doc_url)
        self.general_rating = self.get_general_rating()

    def get_api_with_code_example_ratio(self, example_per_api):
        try:
            number_of_apis = len([api for api in example_per_api if api])
            number_of_apis_with_example = len(
                [eg for eg in example_per_api if len(example_per_api[eg]) > 0])

            return number_of_apis_with_example / number_of_apis
        except ZeroDivisionError:
            return 0

    def get_consistency_ratio(self, matched_signatures, unmatched_signatures):
        try:
            number_of_matched_api = len(matched_signatures)
            number_of_unmatched_api = len(unmatched_signatures)
            number_of_apis = number_of_matched_api + number_of_unmatched_api

            return number_of_matched_api / number_of_apis
        except ZeroDivisionError:
            return 0

    def get_general_rating(self):
        metrics = [self.methods_with_code_examples_ratio * 5,
                   self.classes_with_code_examples_ratio * 5,
                   self.consistency_ratio * 5,
                   (self.text_readability_score / 100) * 5,
                   self.navigability]

        try:
            return round(sum(metrics) / 5)
        except ZeroDivisionError:
            return 0
