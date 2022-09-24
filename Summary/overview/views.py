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
    if "store" not in request.session:
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
                     familiar=familiar,
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
        store["general_rating"] = library_metrics.calculate_general_rating()
        store["description"] = library.description
        store["doc_url"] = library.doc_url
        store["task_list"] = library_metrics.tasks
        store["example_ratios"] = library_metrics.example_ratios
        store["readability_ratios"] = library_metrics.readability_ratios
        store["consistency"] = library_metrics.consistency_ratio
        store["navigability"] = library_metrics.navigability_score
        store["familiar"] = familiar
    request.session["store"] = store
    context = create_overview_context(store)
    return render(request, "overview/overview.html", context)
