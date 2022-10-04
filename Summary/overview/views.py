from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from .Metrics import Metrics
from .forms import Demographics, AnalyzeForm
from .models import Response
from .util import get_groupings, get_library, create_overview_context


def landing(request):
    if request.session.exists(request.session.session_key):
        if "store" in request.session:
            del request.session["store"]
    return render(request, "overview/landing.html",
                  context={"form": AnalyzeForm(),
                           "groupings": get_groupings()
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
    library = get_library(library_name)
    library_metrics = Metrics(library)
    try:
        familiar = Response.objects.get(library_name=library_name,
                                        session_key=request.session.session_key).familiar
    except ObjectDoesNotExist:
        familiar = False
    store = dict(library_name=library_name,
                 language=library.language,
                 doc_url=library.doc_url,
                 general_rating=library_metrics.calculate_general_rating(),
                 description=library.description,
                 task_list=library_metrics.tasks,
                 example_ratios=library_metrics.example_ratios,
                 readability_ratios=library_metrics.readability_ratios,
                 consistency=library_metrics.consistency_ratio,
                 navigability=library_metrics.navigability_score,
                 session_key=request.session.session_key,
                 familiar=familiar)
    if "store" not in request.session:
        store["general_form"] = None
        store["tasks_form"] = None
        store["method_examples_form"] = None
        store["class_examples_form"] = None
        store["text_readability_form"] = None
        store["code_readability_form"] = None
        store["consistency_form"] = None
        store["navigability_form"] = None
        store["feedback_form"] = None
    else:
        store["general_form"] = request.session["store"]["general_form"]
        store["tasks_form"] = request.session["store"]["tasks_form"]
        store["method_examples_form"] = request.session["store"]["method_examples_form"]
        store["class_examples_form"] = request.session["store"]["class_examples_form"]
        store["text_readability_form"] = request.session["store"]["text_readability_form"]
        store["code_readability_form"] = request.session["store"]["code_readability_form"]
        store["consistency_form"] = request.session["store"]["consistency_form"]
        store["navigability_form"] = request.session["store"]["navigability_form"]
        store["feedback_form"] = request.session["store"]["feedback_form"]
    request.session["store"] = store
    context = create_overview_context(store)
    return render(request, "overview/overview.html", context)
