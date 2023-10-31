import os
from urllib.error import URLError

from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError

from doc_quality_analysis_app.forms import AnalyzeForm
from doc_quality_analysis_app.models import Library, Response
from doc_quality_analysis_app.utils.db_utils import get_library, get_groupings
from doc_quality_analysis_app.utils.request_utils import initialize_store
import sys

parent_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append("..")

from analyze_library.lib_analysis_service import analyze_library


def create(request):
    form = AnalyzeForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            language = form.cleaned_data["language"]
            lib_name = form.cleaned_data["library_name"]
            gh_url = form.cleaned_data["gh_url"]
            doc_url = form.cleaned_data["doc_url"]

            try:

                analyze_library(language=language,
                                doc_url=doc_url,
                                gh_url=gh_url,
                                library_name=lib_name)
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                    request.session["store"] = initialize_store(request.session.session_key,
                                                                form.cleaned_data["library_name"])
                return redirect("overview", form.cleaned_data["library_name"])
            # TODO: If there is a problem with the URL then let the user know
            except URLError:
                pass
    return render(request, "landing_page.html",
                  context={"form": form, "groupings": get_groupings()})


def search(request):
    if request.method == "POST":
        try:
            exists = Library.objects.get(
                library_name=request.POST["library_select"])
        except (Library.DoesNotExist, MultiValueDictKeyError):
            exists = False
        if exists:
            if not request.session.exists(request.session.session_key):
                request.session.create()
            request.session["store"] = initialize_store(request.session.session_key, request.POST["library_select"])
            return redirect("overview", request.POST["library_select"])

            # try:
            #     same_user = Response.objects.get(
            #         library_name=request.POST["library_select"],
            #         session_key=request.session.session_key)
            # except (Response.DoesNotExist, MultiValueDictKeyError):
            #     same_user = False
            # if same_user:
            #     return redirect("overview:overview", request.POST["library_select"])
            # else:
            #     if not request.session.exists(request.session.session_key):
            #         request.session.create()
            #     request.session["store"] = initialize_store(request.session.session_key, request.POST["library_select"])
            #     return redirect("overview:overview", request.POST["library_select"])

    return render(request, "landing_page.html",
                  context={"form": AnalyzeForm(),
                           "groupings": get_groupings()
                           })
