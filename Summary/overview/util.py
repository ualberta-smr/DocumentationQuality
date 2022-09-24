from django.forms import ChoiceField

from .models import Library

from .forms import GeneralRating, TaskList, MethodExamples, ClassExamples, \
    TextReadability, CodeReadability, Consistency, Navigability, Feedback


def get_library(library_name):
    return Library.objects.filter(library_name=library_name).get()


def get_groupings():
    libraries = Library.objects.all().values("language", "library_name")
    groupings = dict()
    for library in libraries:
        library_language = library["language"]
        if library_language in groupings:
            groupings[library_language].append(library["library_name"])
        else:
            groupings[library_language] = [library["library_name"]]
    return groupings


def choice_selector(familiar):
    if familiar:
        choices = [(1, "Does not match"),
                   (2, "Somewhat does not match"),
                   (3, "Neither matches nor not matches"),
                   (4, "Somewhat matches"),
                   (5, "Perfectly matches")
                   ]
    else:
        choices = [(1, "Not useful"),
                   (2, "Somewhat not useful"),
                   (3, "Neither useful nor not useful"),
                   (4, "Somewhat useful"),
                   (5, "Very useful")
                   ]
    return choices


def create_form(form, store):
    form({"session_key": store["session_key"],
          "library_name": store["library_name"]})
    for field in form.declared_fields.keys():
        if type(form.declared_fields[field]) == ChoiceField:
            if not form.declared_fields[field].choices:
                form.declared_fields[field].choices = choice_selector(store["familiar"])
    return form


def create_overview_context(store):
    context = {
        "library_name": store["library_name"],
        "language": store["language"],
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
        "general_form": GeneralRating(store["general_form"]) if store["general_form"] else create_form(GeneralRating, store),
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