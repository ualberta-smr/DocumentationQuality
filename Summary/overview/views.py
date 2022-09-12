from django.db.models import Count
from django.shortcuts import render

from .forms import Demographics, GeneralRating, TaskList, MethodExamples, \
    ClassExamples, \
    TextReadability, CodeReadability, Consistency, Navigability, Feedback, \
    AnalyzeForm
from .models import Task, Library, Response


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
    task_list = list(Task.objects.filter(library_name=library_name).values(
        "task", "has_example", "example_page", "paragraph", "html_id").annotate(
        dcount=Count("task")).order_by("-has_example", "-dcount")[:20])

    tasks = []
    for task in task_list:
        paragraph_split = task["paragraph"].split()
        identifier = " ".join(paragraph_split[:5])
        tasks.append(
            {
                "task": task["task"],
                "has_example": task["has_example"],
                "url": task["example_page"] + ("#" + task["html_id"] if task[
                    "html_id"] else "#:~:text=" + identifier)
            })

    return tasks


def _get_consistency_ratio(library):
    ratio = "Could not calculate consistency"

    try:
        ratio = "{:.2%}".format(
            (0.5 * (library.signature_methods / library.methods)) + (
                        0.5 * (library.signature_classes / library.classes)))
    except:
        pass
    return ratio


def _get_example_ratios(library):
    ratios = {
        "method_ratio": "Could not calculate method ratio",
        "class_ratio": "Could not calculate class ratio"
    }
    try:
        try:
            ratios["method_ratio"] = "{:.2%}".format(
                library.method_examples / library.methods)
        except:
            ratios["method_ratio"] = "Calculating..."
        try:
            ratios["class_ratio"] = "{:.2%}".format(
                library.class_examples / library.classes)
        except:
            ratios["class_ratio"] = "Calculating..."
    except:
        pass
    return ratios


def _get_readability_ratios(library):
    ratios = {
        "text_readability": "Could not calculate method ratio",
        "code_readability": "Could not calculate class ratio"
    }
    try:
        try:
            ratios["text_readability"] = library.text_readability_rating
        except:
            ratios["text_readability"] = "Calculating..."
        try:
            if library.code_readability_rating:
                ratios["code_readability"] = library.code_readability_rating
            else:
                ratios["code_readability"] = "N/A"
        except:
            ratios["code_readability"] = "Calculating..."
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
        "readability_ratios": store["readability_ratios"],
        "consistency": store["consistency"],
        "navigability": store["navigability"],
        "session_key": store["session_key"],
        "familiar": store["familiar"],
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
    except Exception as e:
        task_list = []
    try:
        familiar = \
            Response.objects.filter(
                session_key=request.session.session_key).values(
                "familiar").get()["familiar"]
    except:
        familiar = False

    example_ratios = _get_example_ratios(library)
    readability_ratios = _get_readability_ratios(library)
    consistency = _get_consistency_ratio(library)
    if "store" not in request.session:
        store = dict(library_name=library_name,
                     doc_url=library.doc_url,
                     general_rating=3,
                     description=library.description,
                     task_list=task_list,
                     example_ratios=example_ratios,
                     readability_ratios=readability_ratios,
                     consistency=consistency,
                     navigability=2,
                     session_key=request.session.session_key,
                     familiar=False,
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
        store["readability_ratios"] = readability_ratios
        store["consistency"] = consistency
        store["familiar"] = familiar
    request.session["store"] = store
    context = create_overview_context(store)
    return render(request, "overview/overview.html", context)
