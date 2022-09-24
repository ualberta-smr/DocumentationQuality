import json

from analyze.analyze import analyze_library, clone_library
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from .forms import Demographics, GeneralRating, TaskList, MethodExamples, \
    ClassExamples, TextReadability, \
    CodeReadability, Consistency, Navigability, Feedback, AnalyzeForm
from .models import Library, Response
from .util import create_overview_context, get_groupings


def _get_existing_record(request):
    session_key = request.POST["session_key"] if request.POST[
        "session_key"] else request.session.session_key
    library_name = request.POST["library_name"] if request.POST[
        "library_name"] else request.session["store"]["library_name"]
    existing_record, _ = Response.objects.get_or_create(
        session_key=session_key,
        library_name=library_name)
    return existing_record


def search(request):
    if request.method == "POST":
        try:
            exists = Library.objects.get(library_name=request.POST["library_select"])
        except ObjectDoesNotExist:
            exists = False
        if exists:
            try:
                same_user = Response.objects.get(library_name=request.POST["library_select"], session_key=request.session.session_key)
            except ObjectDoesNotExist:
                same_user = False
            if same_user:
                return redirect("overview:overview",
                                request.POST["library_select"])
            else:
                return redirect("overview:demographics",
                                request.POST["library_select"])

    return redirect("overview:landing", context={"form": AnalyzeForm(),
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
                            form.cleaned_data["domain"] if "domain" in form.cleaned_data else None,
                            repo_path)
            if not request.session.exists(request.session.session_key):
                return redirect("overview:demographics",
                                request.POST["library_name"])
            else:
                return redirect("overview:overview",
                                request.POST["library_name"])
    return render(request, "overview/landing.html",
                  context={"form": form, "groupings": get_groupings()})


def demographics_form(request):
    form = Demographics(request.POST)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("overview:overview", request.POST["library_name"])
    return render(request, "overview/forms/demographics_form.html",
                  {"demographics": form})


def general_rating(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = GeneralRating(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["general_form"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.general_rating = request.POST["general_rating"]
                existing_record.save()
            context["general_form"] = form
    return render(request, "overview/overview.html", context)


def task_list(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = TaskList(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["tasks_form"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.task_list = request.POST["task_list"]
                existing_record.save()
            context["tasks_form"] = form
    return render(request, "overview/overview.html", context)


def method_examples(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = MethodExamples(request.POST or None)
        if form.is_valid():
            form.save()
            request.session["store"]["method_examples_form"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.code_examples_methods = request.POST[
                    "code_examples_methods"]
                existing_record.save()
            context["method_examples_form"] = form
    return render(request, "overview/overview.html", context)


def class_examples(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = ClassExamples(request.POST or None)
        if form.is_valid():
            form.save()
            request.session["store"]["class_examples_form"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.code_examples_classes = request.POST[
                    "code_examples_classes"]
                existing_record.save()
            context["class_examples_form"] = form
    return render(request, "overview/overview.html", context)


def text_readability(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = TextReadability(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["text_readability_form"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.text_readability = request.POST[
                    "text_readability"]
                existing_record.save()
            context["text_readability_form"] = form
    return render(request, "overview/overview.html", context)


def code_readability(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = CodeReadability(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["code_readability_form"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.code_readability = request.POST[
                    "code_readability"]
                existing_record.save()
            context["code_readability_form"] = form
    return render(request, "overview/overview.html", context)


def consistency(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Consistency(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["consistency_form"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.consistency = request.POST["consistency"]
                existing_record.save()
            context["consistency_form"] = form
    return render(request, "overview/overview.html", context)


def navigation(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Navigability(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["navigability_form"] = json.dumps(
                form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.navigability = request.POST["navigability"]
                existing_record.save()
            context["navigability_form"] = form
    return render(request, "overview/overview.html", context)


def general(request):
    context = create_overview_context(request.session["store"])
    if request.method == "POST":
        form = Feedback(request.POST)
        if form.is_valid():
            form.save()
            request.session["store"]["feedback_form"] = json.dumps(form.cleaned_data)
            request.session.modified = True
            return redirect("overview:overview", request.POST["library_name"])
        else:
            existing_record = _get_existing_record(request)
            if existing_record:
                existing_record.usefulness = request.POST["usefulness"]
                existing_record.would_recommend = request.POST[
                    "would_recommend"]
                existing_record.general_feedback = request.POST[
                    "general_feedback"]
                existing_record.save()
            context["feedback_form"] = form
    return render(request, "overview/overview.html", context)
