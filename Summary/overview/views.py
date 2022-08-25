import json
import time

from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Count
from django.shortcuts import render, redirect

from Analyze.main import analyze_library
from .models import Task, Library, Response
from .forms import Demographics, GeneralRating, TaskList, CodeExamples, \
    Readability, Consistency, Navigability, Feedback, AnalyzeForm


# Get list of all libraries
def _get_libraries():
    return Library.objects.all().values("library_name")


def _get_library(library_name):
    return Library.objects.filter(library_name=library_name).get()


def _get_task_list(library_name):
    '''
    We do not use HAVING has_example = 1 (.filter(has_example=1)) because that would remove all tasks without an example
    SELECT task, has_example, example_page FROM overview_task WHERE library_name = library_name GROUP BY task ORDER BY has_example DESC, task DESC LIMIT 20
    '''
    return list(Task.objects.filter(library_name=library_name).values(
        "task", "has_example", "example_page").annotate(
        dcount=Count("task")).order_by("-has_example", "-dcount")[:20])


def _get_example_ratios(library_name):
    ratios = {
        "method_ratio": "Could not calculate method ratio",
        "class_ratio": "Could not calculate class ratio"
    }
    try:
        library_data = Library.objects.filter(library_name=library_name).get()
        try:
            ratios["method_ratio"] = "{:.0%}".format(
                library_data.num_method_examples / library_data.num_methods)
        except:
            ratios["method_ratio"] = "N/A"
        try:
            ratios["class_ratio"] = "{:.0%}".format(
                library_data.num_class_examples / library_data.num_classes)
        except:
            ratios["class_ratio"] = "N/A"
    except:
        pass
    return ratios


def _create_overview_context(store):
    context = {
        "library_name": store["library_name"],
        "doc_url": store["doc_url"],
        "general_rating": store["general_rating"],
        "description": store["description"],
        "task_list": store["task_list"],
        "example_ratios": store["example_ratios"],
        "readability": {
            "text_readability": store["readability"]["text_readability"],
            "code_readability": store["readability"]["code_readability"]
        },
        "consistency": store["consistency"],
        "navigation": store["navigation"],
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


def landing(request):
    return render(request, "overview/landing.html",
                  context={"form": AnalyzeForm(),
                           "library_list": _get_libraries()
                           }
                  )


def search(request):
    if request.method == "POST":
        try:
            exists = Library.objects.get(
                library_name=request.POST["library_select"])
        except ObjectDoesNotExist:
            exists = False
        if exists:
            return redirect("overview:overview", request.POST["library_select"])
    return render(request, "overview/landing.html")


def create(request):
    form = AnalyzeForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            analyze_library(form.cleaned_data["language"],
                            form.cleaned_data["library_name"],
                            form.cleaned_data["doc_url"],
                            form.cleaned_data["gh_url"],
                            form.cleaned_data["domain"])
            # Sometimes the redirect happens before the database entry is created, so we sleep
            time.sleep(5)
            return redirect("overview:overview", request.POST["library_name"])
    return render(request, "overview/landing.html", context={"form": form})


def overview(request, library_name):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    library = _get_library(library_name)
    # TODO: These are none before analysis finishes
    try:
        task_list = _get_task_list(library_name)
    except:
        task_list = []

    example_ratios = _get_example_ratios(library)
    if "store" not in request.session:
        store = dict(library_name=library_name,
                     doc_url=library.doc_url,
                     general_rating=3,
                     description=library.description,
                     task_list=task_list,
                     example_ratios=example_ratios,
                     readability={
                         "text_readability": 4,
                         "code_readability": 3
                     },
                     consistency=3,
                     navigation=2,
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
        store["description"] = library.description
        store["doc_url"] = library.doc_url
        store["task_list"] = task_list
        store["example_ratios"] = example_ratios
    request.session["store"] = store
    context = _create_overview_context(store)
    return render(request, "overview/overview.html", context)


def demographics(request, *args, **kwargs):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Demographics(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["demographics"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            context["demographics"] = form
    return render(request, "overview/overview.html", context)


def general_rating(request, *args, **kwargs):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = GeneralRating(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["general"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.general_rating = request.POST["general_rating"]
                existing_record.save()
            context["general"] = form
    return render(request, "overview/overview.html", context)


def task_list(request, *args, **kwargs):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = TaskList(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["tasks"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.task_list = request.POST["task_list"]
                existing_record.save()
            context["tasks"] = form
    return render(request, "overview/overview.html", context)


def code_examples(request):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = CodeExamples(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["examples"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.code_examples_methods = request.POST[
                    "code_examples_methods"]
                existing_record.code_examples_classes = request.POST[
                    "code_examples_classes"]
                existing_record.save()
            context["examples"] = form
    return render(request, "overview/overview.html", context)


def readability(request):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Readability(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["readable"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.text_readability = request.POST[
                    "text_readability"]
                existing_record.code_readability = request.POST[
                    "code_readability"]
                existing_record.save()
            context["readable"] = form
    return render(request, "overview/overview.html", context)


def consistency(request):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Consistency(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["consistent"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.consistency = request.POST["consistency"]
                existing_record.save()
            context["consistent"] = form
    return render(request, "overview/overview.html", context)


def navigation(request):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Navigability(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["navigable"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.navigability = request.POST["navigability"]
                existing_record.save()
            context["navigable"] = form
    return render(request, "overview/overview.html", context)


def general(request):
    context = _create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Feedback(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["feedback"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record, _ = Response.objects.get_or_create(
                session_key=request.POST["session_key"],
                library_name=request.POST["library_name"])
            if existing_record:
                existing_record.usefulness = request.POST["usefulness"]
                existing_record.would_recommend = request.POST[
                    "would_recommend"]
                existing_record.general_feedback = request.POST[
                    "general_feedback"]
                existing_record.save()
            context["feedback"] = form
    return render(request, "overview/overview.html", context)
