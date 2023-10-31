from django.db import models

# Create your models here.

import datetime


class Library(models.Model):
    library_name = models.CharField(max_length=50)
    language = models.CharField(max_length=20)
    description = models.CharField(max_length=1000, blank=True, default="")
    gh_url = models.CharField(max_length=100, blank=True, null=True)
    doc_url = models.CharField(max_length=100)
    task_list_done = models.BooleanField(default=False)
    doc_api_consistency_ratio = models.DecimalField("number of documented methods and classes found in source",
                                                    max_digits=5, decimal_places=3, blank=True, null=True)
    matched_doc_api_len = models.IntegerField("number of doc API found in source code", blank=True, null=True)
    unmatched_doc_api_len = models.IntegerField("number of doc API not found in source code", blank=True, null=True)
    unmatched_doc_api = models.TextField(max_length=50000, blank=True, null=True)
    methods_with_code_examples_ratio = models.DecimalField("number of methods with documented examples",
                                                           max_digits=5, decimal_places=3, blank=True, null=True)
    classes_with_code_examples_ratio = models.DecimalField("number of classes with documented examples", blank=True,
                                                           max_digits=5, decimal_places=3, null=True)
    documented_methods = models.IntegerField("number of methods found in documentation", blank=True, null=True)
    documented_classes = models.IntegerField("number of classes found in documentation", blank=True, null=True)
    text_readability_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    text_readability_rating = models.CharField(max_length=20, blank=True, null=True)
    code_readability_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    code_readability_rating = models.CharField(max_length=20, blank=True, null=True)
    navigability_score = models.CharField(max_length=500, blank=True, null=True)
    general_rating = models.CharField(max_length=500, blank=True, null=True)
    last_updated = models.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return self.library_name


class Response(models.Model):
    session_key = models.CharField(max_length=64)
    library_name = models.CharField(max_length=100)
    years_experience = models.PositiveIntegerField("Years of software development experience", blank=True, null=True)
    familiar = models.BooleanField("familiar", blank=True, null=True)
    general_rating = models.CharField(max_length=100, blank=True, null=True)
    task_list = models.CharField(max_length=100, blank=True, null=True)
    code_examples_methods = models.CharField(max_length=100, blank=True, null=True)
    code_examples_classes = models.CharField(max_length=100, blank=True, null=True)
    text_readability = models.CharField(max_length=100, blank=True, null=True)
    code_readability = models.CharField(max_length=100, blank=True, null=True)
    consistency = models.CharField(max_length=100, blank=True, null=True)
    navigability = models.CharField(max_length=100, blank=True, null=True)

    usefulness = models.CharField(max_length=100, blank=True, null=True)
    where_see = models.CharField(max_length=100, blank=True, null=True)
    matching = models.CharField(max_length=100, blank=True, null=True)
    general_feedback = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session_key", "library_name"], name="unique_session_library_combination")
        ]
