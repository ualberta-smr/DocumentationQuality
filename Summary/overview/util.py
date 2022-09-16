from .models import Library

from .forms import GeneralRating, TaskList, MethodExamples, ClassExamples, \
    TextReadability, CodeReadability, Consistency, Navigability, Feedback


def get_libraries():
    return Library.objects.all().values("language", "library_name")


def get_library(library_name):
    return Library.objects.filter(library_name=library_name).get()


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