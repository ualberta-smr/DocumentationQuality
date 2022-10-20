import json
from urllib.error import URLError

from analyze.analyze import analyze_library, clone_library
from http import HTTPStatus
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError

from .forms import Demographics, GeneralRating, TaskList, MethodExamples, \
    ClassExamples, TextReadability, \
    CodeReadability, Consistency, Navigability, Feedback, AnalyzeForm, Survey
from .models import Library, Response, Task
from .util import get_groupings, initialize_store


def _get_or_create_existing_response(request):
    session_key = request.POST["session_key"] if request.POST[
        "session_key"] else request.session.session_key
    library_name = request.POST["library_name"] if request.POST[
        "library_name"] else request.session["store"]["library_name"]
    existing_record, _ = Response.objects.get_or_create(
        session_key=session_key,
        library_name=library_name)
    return existing_record


def _get_existing_response(request):
    session_key = request.POST["session_key"] if request.POST[
        "session_key"] else request.session.session_key
    library_name = request.POST["library_name"] if request.POST[
        "library_name"] else request.session["store"]["library_name"]
    existing_record = Response.objects.get(session_key=session_key,
                                           library_name=library_name)
    return existing_record


def check(request, library_name):
    checks = Library.objects.values("language", "task_list_done", "methods", "classes", "text_readability_score", "code_readability_score", "navigability").get(library_name=library_name)
    success = True
    for key, value in checks.items():
        if value is None:
            if key == "code_readability_score" and checks["language"] != "java":
                pass
            else:
                success = False
    if success:
        return HttpResponse("", status=HTTPStatus.OK)
    else:
        return HttpResponse("", status=HTTPStatus.INTERNAL_SERVER_ERROR)


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
                return redirect("overview:overview", request.POST["library_select"])
            else:
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                request.session["store"] = initialize_store(request.session.session_key, request.POST["library_select"])
                return redirect("overview:overview", request.POST["library_select"])

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
            try:
                analyze_library(form.cleaned_data["language"],
                                form.cleaned_data["library_name"],
                                form.cleaned_data["doc_url"],
                                form.cleaned_data["gh_url"],
                                form.cleaned_data["domain"] if "domain" in form.cleaned_data else None,
                                repo_path)
                if not request.session.exists(request.session.session_key):
                    request.session.create()
                    request.session["store"] = initialize_store(request.session.session_key, form.cleaned_data["library_name"])
                return redirect("overview:overview", form.cleaned_data["library_name"])
            # TODO: If there is a problem with the URL then let the user know
            except URLError:
                pass
    return render(request, "overview/landing.html",
                  context={"form": form, "groupings": get_groupings()})


def demographics_form(request, library_name):
    if request.method == "POST":
        form = Demographics(request.POST)
        if form.is_valid():
            form.save()
        if not request.session.exists(request.session.session_key):
            request.session.create()
            print(
                "--------------------------------------------------------------------------------Created Session in demographics------------------------------------------------------------------")
        if "store" not in request.session:
            request.session["store"] = initialize_store(
                request.session.session_key,
                library_name)
            print(
                "--------------------------------------------------------------------------------Created store in demographics------------------------------------------------------------------")
        data = {"session_key": request.session["store"]["session_key"],
                "library_name": request.session["store"]["library_name"],
                "familiar": form.cleaned_data["familiar"] if "familiar" in form.cleaned_data else "",
                "years_experience": form.cleaned_data["years_experience"] if "years_experience" in form.cleaned_data else ""
                }
        request.session["store"]["demographics_form"] = json.dumps(data)
        request.session.modified = True
    return redirect("overview:overview", request.POST["library_name"])


def survey_form(request):
    if request.method == "POST":
        form = Survey(request.POST)
        data = dict()
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_response(request)
            if existing_record:
                data["session_key"] = form.cleaned_data["session_key"]
                data["library_name"] = form.cleaned_data["library_name"]
                for key in form.declared_fields.keys():
                    if key != "session_key" and key != "library_name":
                        if key in form.cleaned_data and form.cleaned_data[key]:
                            data[key] = form.cleaned_data[key]
                            setattr(existing_record, key, form.cleaned_data[key])
                        elif key in form.data and form.data[key]:
                            if key == "where_see":
                                data[key] = form.data[key]
                                setattr(existing_record, key, str(form.data[key]))
                existing_record.save()
        request.session["store"]["survey_form"] = json.dumps(data) if data else json.dumps(form.cleaned_data)
        request.session.modified = True
    return HttpResponse(status=204)
    # return redirect("overview:overview", request.POST["library_name"])


def general_rating(request):
    if request.method == "POST":
        form = GeneralRating(request.POST)
        if form.is_valid():
            form.save()
        else:
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
            existing_record = _get_or_create_existing_response(request)
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
