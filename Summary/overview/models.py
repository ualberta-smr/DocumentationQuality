import datetime

from django.db import models


class Library(models.Model):
    library_name = models.CharField(max_length=50)
    language = models.CharField(max_length=20)
    domain = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=1000)
    gh_url = models.CharField(max_length=100, blank=True, null=True)
    doc_url = models.CharField(max_length=100)
    method_examples = models.IntegerField("number of methods with documentation examples", blank=True, null=True)
    methods = models.IntegerField("number of methods", blank=True,null=True)
    class_examples = models.IntegerField("number of classes with documentation examples", blank=True, null=True)
    classes = models.IntegerField("number of classes", blank=True,null=True)
    signature_methods = models.IntegerField("number of methods found in documentation", blank=True, null=True)
    signature_classes = models.IntegerField("number of classes found in documentation", blank=True, null=True)
    text_readability_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    text_readability_rating = models.CharField(max_length=20, blank=True, null=True)
    code_readability_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    code_readability_rating = models.CharField(max_length=20, blank=True, null=True)
    navigability = models.CharField(max_length=500, blank=True, null=True)
    last_updated = models.DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return self.library_name


class Task(models.Model):
    library_name = models.CharField(max_length=50)
    # library = models.ForeignKey(Library, on_delete=models.CASCADE)
    paragraph = models.CharField(max_length=5000)
    task = models.CharField(max_length=100)
    has_example = models.BooleanField("has example")
    example_page = models.CharField(max_length=100)
    html_id = models.CharField(max_length=500)

    def __str__(self):
        return self.task


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