import json

from django.db.models import Count
from django.shortcuts import render, redirect

from .models import Task, Library, Response
from .survey import Demographics, GeneralRating, TaskList, CodeExamples, \
    Readability, Consistency, Navigability, Feedback


def _get_task_list(library_name):
    return list(Task.objects.filter(library_name=library_name).values(
        "task", "has_example", "example_page").annotate(
        dcount=Count("task")).order_by("-dcount", "task")[:20])


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


def _create_context(store):
    context = {
        "library_name": store["library_name"],
        "general_rating": 3,
        "license": "MIT",
        "task_list": store["task_list"],
        "example_ratios": store["example_ratios"],
        "readability": {
            "text_readability": 4,
            "code_readability": 3
        },
        "consistency": 3,
        "navigation": 2,
        "session_key": store["session_key"],
        "have_demographics": True if store["demographics"] else False,
        "demographics": Demographics(store["demographics"]) if store[
            "demographics"] else Demographics(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "general": GeneralRating(store["general"]) if store[
            "general"] else GeneralRating({"session_key": store["session_key"],
                                           "library_name": store[
                                               "library_name"]}),
        "tasks": TaskList(store["tasks"]) if store["tasks"] else TaskList(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "examples": CodeExamples(store["examples"]) if store[
            "examples"] else CodeExamples({"session_key": store["session_key"],
                                           "library_name": store[
                                               "library_name"]}),
        "readable": Readability(store["readable"]) if store[
            "readable"] else Readability({"session_key": store["session_key"],
                                          "library_name": store[
                                              "library_name"]}),
        "consistent": Consistency(store["consistent"]) if store[
            "consistent"] else Consistency({"session_key": store["session_key"],
                                            "library_name": store[
                                                "library_name"]}),
        "navigable": Navigability(store["navigable"]) if store[
            "navigable"] else Navigability({"session_key": store["session_key"],
                                            "library_name": store[
                                                "library_name"]}),
        "feedback": Feedback(store["feedback"]) if store[
            "feedback"] else Feedback({"session_key": store["session_key"],
                                       "library_name": store["library_name"]})
    }
    return context


def overview(request, library_name):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    task_list = _get_task_list(library_name)
    example_ratios = _get_example_ratios(library_name)

    if "store" not in request.session:
        store = dict(library_name=library_name,
                     general_rating=3,
                     license="MIT",
                     task_list=task_list,
                     example_ratios=example_ratios,
                     readability={
                         "text_readability": 4,
                         "code_readability": 3
                     },
                     consistency=3, navigation=2,
                     session_key=request.session.session_key,
                     demographics=None,
                     general=None,
                     tasks=None,
                     examples=None,
                     readable=None,
                     consistent=None,
                     navigable=None,
                     feedback=None)
    else:
        store = request.session["store"]
        store["task_list"] = task_list
        store["example_ratios"] = example_ratios
    request.session["store"] = store
    context = _create_context(store)
    return render(request, "overview/overview.html", context)


def demographics(request, *args, **kwargs):
    if request.method == "POST":
        form = Demographics(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["demographics"] = json.dumps(
                    form.cleaned_data)
            request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def general(request, *args, **kwargs):
    if request.method == "POST":
        form = GeneralRating(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["general"] = json.dumps(form.cleaned_data)
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.general_rating = request.POST["general_rating"]
                existing_record.save()
    return redirect("overview:overview", request.POST["library_name"])
