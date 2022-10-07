import json

from analyze.analyze import analyze_library, clone_library
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError

from .forms import Demographics, GeneralRating, TaskList, MethodExamples, \
    ClassExamples, TextReadability, \
    CodeReadability, Consistency, Navigability, Feedback, AnalyzeForm
from .models import Library, Response
from .util import get_groupings, initialize_store


def _get_or_create_existing_record(request):
    session_key = request.POST["session_key"] if request.POST[
        "session_key"] else request.session.session_key
    library_name = request.POST["library_name"] if request.POST[
        "library_name"] else request.session["store"]["library_name"]
    existing_record, _ = Response.objects.get_or_create(
        session_key=session_key,
        library_name=library_name)
    return existing_record


def _get_existing_record(request):
    session_key = request.POST["session_key"] if request.POST[
        "session_key"] else request.session.session_key
    library_name = request.POST["library_name"] if request.POST[
        "library_name"] else request.session["store"]["library_name"]
    existing_record = Response.objects.get(session_key=session_key,
                                           library_name=library_name)
    return existing_record


def search(request):
    if request.method == "POST":
        try:
            exists = Library.objects.get(
                library_name=request.POST["library_select"])
        except (Library.DoesNotExist, MultiValueDictKeyError):
            exists = False
        if exists:
            try:
                same_user = Response.objects.get(
                    library_name=request.POST["library_select"],
                    session_key=request.session.session_key)
            except (Response.DoesNotExist, MultiValueDictKeyError):
                same_user = False
            if same_user:
                return redirect("overview:overview",
                                request.POST["library_select"])
            else:
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                request.session["store"] = initialize_store(
                    request.session.session_key,
                    request.POST["library_select"])
                return render(request, "overview/forms/demographics_form.html",
                              {"library_name": request.session["store"][
                                  "library_name"],
                               "demographics": Demographics()})

    return render(request, "overview/landing.html",
                  context={"form": AnalyzeForm(),
                           "groupings": get_groupings()
                           })


def create(request):
    form = AnalyzeForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            repo_path = clone_library(form.cleaned_data["library_name"],
                                      form.cleaned_data["gh_url"])
            analyze_library(form.cleaned_data["language"],
                            form.cleaned_data["library_name"],
                            form.cleaned_data["doc_url"],
                            form.cleaned_data["gh_url"],
                            form.cleaned_data[
                                "domain"] if "domain" in form.cleaned_data else None,
                            repo_path)
            if not request.session.exists(request.session.session_key):
                request.session.create()
                request.session["store"] = initialize_store(
                    request.session.session_key, request.POST["library_name"])
                return render(request, "overview/forms/demographics_form.html",
                              {"library_name": request.session["store"][
                                  "library_name"],
                               "demographics": Demographics()})
            else:
                return redirect("overview:overview",
                                request.POST["library_name"])
    return render(request, "overview/landing.html",
                  context={"form": form, "groupings": get_groupings()})


def demographics_form(request):
    updated_request = request.POST.copy()
    updated_request.update({
        "session_key": request.session["store"]["session_key"],
        "library_name": request.session["store"]["library_name"]
    })
    form = Demographics(updated_request)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("overview:overview",
                            updated_request["library_name"])
        else:
            try:
                existing_record = _get_existing_record(request)
            except Response.DoesNotExist:
                existing_record = False
            if existing_record:
                return redirect("overview:overview",
                                updated_request["library_name"])
    return render(request, "overview/forms/demographics_form.html",
                  {"library_name": updated_request["library_name"],
                      "demographics": form})


def general_rating(request):
    if request.method == "POST":
        form = GeneralRating(request.POST)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.general_rating = request.POST["general_rating"]
                existing_record.save()
        request.session["store"]["general_form"] = json.dumps(form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def task_list(request):
    if request.method == "POST":
        form = TaskList(request.POST)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.task_list = request.POST["task_list"]
                existing_record.save()
        request.session["store"]["tasks_form"] = json.dumps(form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def method_examples(request):
    if request.method == "POST":
        form = MethodExamples(request.POST or None)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.code_examples_methods = request.POST[
                    "code_examples_methods"]
                existing_record.save()
        request.session["store"]["method_examples_form"] = json.dumps(
            form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def class_examples(request):
    if request.method == "POST":
        form = ClassExamples(request.POST or None)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.code_examples_classes = request.POST[
                    "code_examples_classes"]
                existing_record.save()
        request.session["store"]["class_examples_form"] = json.dumps(
            form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def text_readability(request):
    if request.method == "POST":
        form = TextReadability(request.POST)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.text_readability = request.POST[
                    "text_readability"]
                existing_record.save()
        request.session["store"]["text_readability_form"] = json.dumps(
            form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def code_readability(request):
    if request.method == "POST":
        form = CodeReadability(request.POST)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.code_readability = request.POST[
                    "code_readability"]
                existing_record.save()
        request.session["store"]["code_readability_form"] = json.dumps(
            form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def consistency(request):
    if request.method == "POST":
        form = Consistency(request.POST)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.consistency = request.POST["consistency"]
                existing_record.save()
        request.session["store"]["consistency_form"] = json.dumps(
            form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def navigation(request):
    if request.method == "POST":
        form = Navigability(request.POST)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.navigability = request.POST["navigability"]
                existing_record.save()
        request.session["store"]["navigability_form"] = json.dumps(
            form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def general(request):
    if request.method == "POST":
        form = Feedback(request.POST)
        if form.is_valid():
            form.save()

        else:
            existing_record = _get_or_create_existing_record(request)
            if existing_record:
                existing_record.usefulness = request.POST["usefulness"]
                existing_record.would_recommend = request.POST[
                    "would_recommend"]
                existing_record.general_feedback = request.POST[
                    "general_feedback"]
                existing_record.save()
        request.session["store"]["feedback_form"] = json.dumps(
            form.cleaned_data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])
