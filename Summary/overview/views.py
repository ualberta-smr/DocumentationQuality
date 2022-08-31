from django.db.models import Count
from django.shortcuts import render

from .forms import Demographics, GeneralRating, TaskList, MethodExamples, \
    ClassExamples, \
    TextReadability, CodeReadability, Consistency, Navigability, Feedback, \
    AnalyzeForm
from .models import Task, Library


# Get list of all libraries
def _get_libraries():
    return Library.objects.all().values("language", "library_name")


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
            ratios["method_ratio"] = "Calculating..."
        try:
            ratios["class_ratio"] = "{:.0%}".format(
                library_data.num_class_examples / library_data.num_classes)
        except:
            ratios["class_ratio"] = "Calculating..."
    except:
        pass
    return ratios


def create_overview_context(store):
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
        "general": GeneralRating(store["general"]) if store[
            "general"] else GeneralRating({"session_key": store["session_key"],
                                           "library_name": store[
                                               "library_name"]}),
        "tasks": TaskList(store["tasks"]) if store["tasks"] else TaskList(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "method_examples": MethodExamples(store["method_examples"]) if store[
            "method_examples"] else MethodExamples(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "class_examples": ClassExamples(store["class_examples"]) if store[
            "class_examples"] else ClassExamples(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "text_readability": TextReadability(store["text_readability"]) if store[
            "text_readability"] else TextReadability(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "code_readability": CodeReadability(store["code_readability"]) if store[
            "code_readability"] else CodeReadability(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
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
    if request.session.exists(request.session.session_key):
        if "store" in request.session:
            del request.session["store"]
    libraries = _get_libraries()
    groupings = dict()
    for library in libraries:
        library_language = library["language"]
        if library_language in groupings:
            groupings[library_language].append(library["library_name"])
        else:
            groupings[library_language] = [library["library_name"]]
    return render(request, "overview/landing.html",
                  context={"form": AnalyzeForm(),
                           "groupings": groupings
                           }
                  )


def demographics(request, library_name):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    return render(request, "overview/forms/demographics_form.html", {
        "demographics": Demographics(
            {"session_key": request.session.session_key,
             "library_name": library_name})})


def overview(request, library_name):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    library = _get_library(library_name)
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
                     general=None,
                     tasks=None,
                     method_examples=None,
                     class_examples=None,
                     text_readability=None,
                     code_readability=None,
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
    context = create_overview_context(store)
    return render(request, "overview/overview.html", context)
