from django.forms import ChoiceField

from .models import Library

from .forms import GeneralRating, TaskList, MethodExamples, ClassExamples, \
    TextReadability, CodeReadability, Consistency, Navigability, Feedback


def get_libraries():
    return Library.objects.all().values("language", "library_name")


def get_library(library_name):
    return Library.objects.filter(library_name=library_name).get()


def choice_selector(familiar):
    if familiar:
        choices = [(1, "1"),
                   (2, "2"),
                   (3, "3"),
                   (4, "4"),
                   (5, "5")
                   ]
    else:
        choices = [(1, "Unuseful"),
                   (2, "Somewhat unuseful"),
                   (3, "Neither useful nor unuseful"),
                   (4, "Somewhat useful"),
                   (5, "Very useful")
                   ]
    return choices


def create_form(form, store):
    form({"session_key": store["session_key"],
          "library_name": store["library_name"]})
    for field in form.declared_fields.keys():
        if type(form.declared_fields[field]) == ChoiceField:
            form.declared_fields[field].choices = choice_selector(store["familiar"])
    return form


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
        "tasks_form": TaskList(store["tasks_form"]) if store["tasks_form"] else create_form(TaskList, store),
        "method_examples_form": MethodExamples(store["method_examples_form"]) if store["method_examples_form"] else create_form(MethodExamples, store),
        "class_examples_form": ClassExamples(store["class_examples_form"]) if store["class_examples_form"] else create_form(ClassExamples, store),
        "text_readability_form": TextReadability(store["text_readability_form"]) if store["text_readability_form"] else create_form(TextReadability, store),
        "code_readability_form": CodeReadability(store["code_readability_form"]) if store["code_readability_form"] else create_form(CodeReadability, store),
        "consistency_form": Consistency(store["consistency_form"]) if store["consistency_form"] else create_form(Consistency, store),
        "navigability_form": Navigability(store["navigability_form"]) if store["navigability_form"] else create_form(Navigability, store),
        "feedback_form": Feedback(store["feedback_form"]) if store["feedback_form"] else create_form(Feedback, store)
    }
    return context