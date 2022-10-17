import json

from django.db.models import Count

from .models import Task


class Metrics:
    def __init__(self, library):
        self.library = library
        self.tasks = self._get_task_list()
        self.example_ratios = self._get_example_ratios()
        self.readability_ratios = self._get_readability_ratios()
        self.consistency_ratio = self._get_consistency_ratio()
        self.navigability_score = self._get_navigability_score()

    def _create_url(self, task):
        url = []
        if task["example_page"]:
            url.append(task["example_page"])
            url.append("#")
            if task["html_id"]:
                url.append(task["html_id"])
            else:
                url.append(":~:text=")
                url.append(" ".join(task["paragraph"].split()[:5]))
        else:
            url.append(self.library.doc_url)

        return ''.join(url)

    def _get_task_list(self):
        '''
        We do not use HAVING has_example = 1 (.filter(has_example=1)) because that would remove all tasks without an example
        SELECT task, has_example, example_page FROM overview_task WHERE library_name = library_name GROUP BY task ORDER BY has_example DESC, task DESC LIMIT 20
        '''
        task_list = list(
            Task.objects.filter(library_name=self.library.library_name).values(
                "task", "has_example", "example_page", "paragraph",
                "html_id").annotate(
                dcount=Count("task")).order_by("-has_example", "-dcount")[:20])

        tasks = []
        for task in task_list:
            tasks.append(
                {
                    "task": task["task"],
                    "has_example": task["has_example"],
                    "url": self._create_url(task)
                })

        return tasks

    def _get_example_ratios(self):
        ratios = {
            "method_ratio": 0,
            "class_ratio": 0
        }

        try:
            ratios["method_ratio"] = round((self.library.method_examples /
                                      self.library.methods) * 5)
        except (TypeError, AttributeError, ZeroDivisionError):
            pass
        try:
            ratios["class_ratio"] = round((self.library.class_examples /
                                     self.library.classes) * 5)
        except (TypeError, AttributeError, ZeroDivisionError):
            pass
        return ratios

    def _get_readability_ratios(self):
        ratios = {
            "text_readability": 0,
            "code_readability": 0
        }

        try:
            ratios["text_readability"] = round((self.library.text_readability_score
                                          / 100) * 5)
        except (TypeError, AttributeError):
            pass
        try:
            ratios["code_readability"] = round((self.library.code_readability_score
                                          / 100) * 5)
        except(TypeError, AttributeError):
            pass

        return ratios

    def _get_consistency_ratio(self):
        ratio = 0
        try:
            ratio = ((0.5 * (self.library.signature_methods
                             / self.library.methods)) +
                     (0.5 * (self.library.signature_classes
                             / self.library.classes))
                     ) * 5
        except (TypeError, AttributeError, ZeroDivisionError):
            pass
        return round(ratio)

    def _get_navigability_score(self):
        rating = 0
        if self.library.navigability:
            nav_checks = json.loads(self.library.navigability)
            count = 0
            for check in nav_checks:
                if check:
                    count += 1
            if count > 1:
                rating = 5
            elif count > 0:
                rating = 3
        return rating

    def calculate_general_rating(self):
        metrics = [self.example_ratios["method_ratio"],
                   self.example_ratios["class_ratio"],
                   self.readability_ratios["text_readability"],
                   self.consistency_ratio,
                   self.navigability_score]
        if self.library.language.lower() == "java":
            metrics.append(self.readability_ratios["code_readability"])
        return round(sum(metrics) / len(metrics))
