from django.db import models


# Create your models here.


class Task(models.Model):
    library_name = models.CharField(max_length=50)
    paragraph = models.CharField(max_length=5000)
    task = models.CharField(max_length=100)
    has_example = models.BooleanField("has example")
    example_page = models.CharField(max_length=100)

    def __str__(self):
        return self.task


class Library(models.Model):
    library_name = models.CharField(max_length=50)
    gh_url = models.CharField(max_length=100)
    doc_url = models.CharField(max_length=100)
    num_methods = models.IntegerField("number of methods")
    num_classes = models.IntegerField("number of classes")
    num_method_examples = models.IntegerField(
        "number of methods with documentation examples")
    num_class_examples = models.IntegerField(
        "number of classes with documentation examples")

    def __str__(self):
        return self.library_name