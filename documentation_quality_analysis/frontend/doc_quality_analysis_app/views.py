from django.shortcuts import render, HttpResponse

from doc_quality_analysis_app.forms import AnalyzeForm
from doc_quality_analysis_app.models import Response, Library
from doc_quality_analysis_app.utils.db_utils import get_library, get_groupings
from doc_quality_analysis_app.utils.request_utils import initialize_store, update_store, create_overview_context


# Create your views here.
def home(request):
    return render(request, 'overview1.html')


def landing(request):
    if request.session.exists(request.session.session_key):
        if "store" in request.session:
            del request.session["store"]
    return render(request, "landing_page.html",
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
    library: Library = get_library(library_name)
    # library_metrics = Metrics(library)
    try:
        response = Response.objects.get(library_name=library_name,
                                        session_key=request.session.session_key)
        show_demographic_form = False
        familiar = response.familiar
        # try:
        #     if not request.session["store"]["survey_form"]:
        #         form = dict()
        #         for field in response._meta.get_fields():
        #             if field.name != "id":
        #                 form[field.name] = getattr(response, field.name)
        #         request.session["store"]["survey_form"] = json.dumps(form)
        # except MultiValueDictKeyError:
        #     pass
    except Response.DoesNotExist:
        show_demographic_form = True
        familiar = False

    values = {
        "language": library.language,
        "doc_url": library.doc_url,
        "gh_url": library.gh_url,
        "general_rating": library.general_rating,
        # "description": library.description,
        # "task_list": library_metrics.tasks,
        "example_ratios": {'method_ratio': round(library.methods_with_code_examples_ratio*5),
                           'class_ratio': round(library.classes_with_code_examples_ratio*5)},
        # "method_example_ratios": library.methods_with_code_examples,
        # "class_example_ratios": library.classes_with_code_examples,
        "readability_ratios": {'text_readability': round((library.text_readability_score/100)*5),
                               'code_readability': None},
        "consistency": round(library.doc_api_consistency_ratio*5),
        "navigability": library.navigability_score,
        # "familiar": familiar,
        # "show_demographic_form": show_demographic_form,
        # "survey_form": request.session["store"]["survey_form"],
        # "demographics_form": request.session["store"]["demographics_form"],
        # "general_form": request.session["store"]["general_form"],
        # "tasks_form": request.session["store"]["tasks_form"],
        # "method_examples_form": request.session["store"]["method_examples_form"],
        # "class_examples_form": request.session["store"]["class_examples_form"],
        # "text_readability_form": request.session["store"]["text_readability_form"],
        # "code_readability_form": request.session["store"]["code_readability_form"],
        # "consistency_form": request.session["store"]["consistency_form"],
        # "navigability_form": request.session["store"]["navigability_form"],
        # "feedback_form": request.session["store"]["feedback_form"]
    }
    request.session["store"] = update_store(request.session["store"], values)
    context = create_overview_context(request.session["store"])
    return render(request, "lib_overview.html", context)

