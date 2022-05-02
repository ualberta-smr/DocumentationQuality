from django.shortcuts import render
from django.db.models import Count
from .models import Task, Library


def _get_task_list(library_name):
    return Task.objects.filter(library_name=library_name).values(
        "task", "has_example", "example_page").annotate(dcount=Count("task")).order_by("-dcount", "task")[:20]


def _get_example_ratios(library_name):
    library_data = Library.objects.filter(library_name=library_name).get()
    ratios = {
        "method_ratio": "Could not calculate method ratio",
        "class_ratio": "Could not calculate class ratio"
    }
    try:
        ratios["method_ratio"] = "{:.0%}".format(
            library_data.num_method_examples / library_data.num_methods)
    except ZeroDivisionError:
        ratios["method_ratio"] = "No methods found in library source code"
    try:
        ratios["class_ratio"] = "{:.0%}".format(
            library_data.num_class_examples / library_data.num_classes)
    except ZeroDivisionError:
        ratios["class_ratio"] = "No methods found in library source code"
    return ratios


def overview(request, library_name):
    task_list = _get_task_list(library_name)
    example_ratios = _get_example_ratios(library_name)

    context = {
        "library_name": library_name,
        "general_rating": 3,
        "license": "MIT",
        "task_list": task_list,
        "example_ratios": example_ratios,
        "text_readability": 4,
        "code_readability": 3,
        "consistency": 3,
        "navigation": 2
    }
    return render(request, "overview/overview.html", context)
