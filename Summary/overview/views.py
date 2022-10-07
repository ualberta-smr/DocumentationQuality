from django.shortcuts import render
from .Metrics import Metrics
from .forms import AnalyzeForm
from .models import Response
from .util import get_groupings, get_library, create_overview_context, \
    initialize_store, update_store


def landing(request):
    if request.session.exists(request.session.session_key):
        if "store" in request.session:
            del request.session["store"]
    return render(request, "overview/landing.html",
                  context={"form": AnalyzeForm(),
                           "groupings": get_groupings()
                           }
                  )


def overview(request, library_name):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    if "store" not in request.session:
        request.session["store"] = initialize_store(request.session.session_key,
                                                library_name)
    library = get_library(library_name)
    library_metrics = Metrics(library)
    try:
        familiar = Response.objects.get(library_name=library_name,
                                        session_key=request.session.session_key).familiar
    except Response.DoesNotExist:
        familiar = False
    values = {
        "language": library.language,
        "doc_url": library.doc_url,
        "general_rating": library_metrics.calculate_general_rating(),
        "description": library.description,
        "task_list": library_metrics.tasks,
        "example_ratios": library_metrics.example_ratios,
        "readability_ratios": library_metrics.readability_ratios,
        "consistency": library_metrics.consistency_ratio,
        "navigability": library_metrics.navigability_score,
        "familiar": familiar,
        "general_form": request.session["store"]["general_form"],
        "tasks_form": request.session["store"]["tasks_form"],
        "method_examples_form": request.session["store"]["method_examples_form"],
        "class_examples_form": request.session["store"]["class_examples_form"],
        "text_readability_form": request.session["store"]["text_readability_form"],
        "code_readability_form": request.session["store"]["code_readability_form"],
        "consistency_form": request.session["store"]["consistency_form"],
        "navigability_form": request.session["store"]["navigability_form"],
        "feedback_form": request.session["store"]["feedback_form"]
    }
    request.session["store"] = update_store(request.session["store"], values)
    context = create_overview_context(request.session["store"])
    return render(request, "overview/overview.html", context)
