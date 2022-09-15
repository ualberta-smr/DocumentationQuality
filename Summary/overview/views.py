import json

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
    ratio = 0
    try:
        ratio = ((0.5 * (library.signature_methods / library.methods)) +
                 (0.5 * (library.signature_classes / library.classes))
                 ) * 5
    except (TypeError, AttributeError, ZeroDivisionError):
        pass
    return ratio


def _get_example_ratios(library):
    ratios = {
        "method_ratio": 0,
        "class_ratio": 0
    }

    try:
        ratios["method_ratio"] = (library.method_examples / library.methods) * 5
    except (TypeError, AttributeError, ZeroDivisionError):
        pass
    try:
        ratios["class_ratio"] = (library.class_examples / library.classes) * 5
    except (TypeError, AttributeError, ZeroDivisionError):
        pass

    return ratios


def _get_readability_ratios(library):
    ratios = {
        "text_readability": 0,
        "code_readability": 0
    }

    try:
        ratios["text_readability"] = (library.text_readability_score / 100) * 5
    except (TypeError, AttributeError):
        pass
    try:
        ratios["code_readability"] = (library.code_readability_score / 100) * 5
    except(TypeError, AttributeError):
        pass

    return ratios


def _get_navigability_score(library):
    rating = 0
    if library.navigability:
        nav_checks = json.loads(library.navigability)
        count = 0
        for check in nav_checks:
            if check:
                count += 1
        if count > 1:
            rating = 5
        elif count > 0:
            rating = 3
    return rating


def _calculate_general_rating(metrics):
    return sum(metrics)/len(metrics) if metrics else 0


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
        "general_form": GeneralRating(store["general_form"]) if
        store["general_form"] else GeneralRating(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "tasks_form": TaskList(store["tasks_form"]) if store[
            "tasks_form"] else TaskList(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "method_examples_form": MethodExamples(store["method_examples_form"]) if
        store["method_examples_form"] else MethodExamples(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "class_examples_form": ClassExamples(store["class_examples_form"]) if
        store["class_examples_form"] else ClassExamples(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "text_readability_form": TextReadability(
            store["text_readability_form"]) if
        store["text_readability_form"] else TextReadability(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "code_readability_form": CodeReadability(
            store["code_readability_form"]) if
        store["code_readability_form"] else CodeReadability(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "consistency_form": Consistency(store["consistency_form"]) if
        store["consistency_form"] else Consistency(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "navigability_form": Navigability(store["navigability_form"]) if
        store["navigability_form"] else Navigability(
            {"session_key": store["session_key"],
             "library_name": store["library_name"]}),
        "feedback_form": Feedback(store["feedback_form"]) if
        store["feedback_form"] else Feedback(
            {"session_key": store["session_key"],
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
    try:
        familiar = Response.objects.filter(
            session_key=request.session.session_key).values(
            "familiar").get()["familiar"]
    except:
        familiar = False

    example_ratios = _get_example_ratios(library)
    readability_ratios = _get_readability_ratios(library)
    consistency = _get_consistency_ratio(library)
    navigability = _get_navigability_score(library)
    metrics = [
        example_ratios["method_ratio"],
        example_ratios["class_ratio"],
        readability_ratios["text_readability"],
        readability_ratios["code_readability"],
        consistency,
        navigability
    ]
    general_rating = _calculate_general_rating(metrics)
    if "store" not in request.session:
        store = dict(library_name=library_name,
                     doc_url=library.doc_url,
                     general_rating=general_rating,
                     description=library.description,
                     task_list=task_list,
                     example_ratios=example_ratios,
                     readability_ratios=readability_ratios,
                     consistency=consistency,
                     navigability=navigability,
                     session_key=request.session.session_key,
                     familiar=False,
                     general_form=None,
                     tasks_form=None,
                     method_examples_form=None,
                     class_examples_form=None,
                     text_readability_form=None,
                     code_readability_form=None,
                     consistency_form=None,
                     navigability_form=None,
                     feedback_form=None)
    else:
        store = request.session["store"]
        store["general_rating"] = general_rating
        store["description"] = library.description
        store["doc_url"] = library.doc_url
        store["task_list"] = task_list
        store["example_ratios"] = example_ratios
        store["readability_ratios"] = readability_ratios
        store["consistency"] = consistency
        store["navigability"] = navigability
        store["familiar"] = familiar
    request.session["store"] = store
    context = create_overview_context(store)
    return render(request, "overview/overview.html", context)
