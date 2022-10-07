import json

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
        library_language = library["language"].capitalize()
        if library_language in groupings:
            groupings[library_language].append(library["library_name"])
        else:
            groupings[library_language] = [library["library_name"]]
    return groupings


UNFAMILIAR_CHOICES = [(1, "Not useful"),
                      (2, "Somewhat not useful"),
                      (3, "Neither useful nor not useful"),
                      (4, "Somewhat useful"),
                      (5, "Very useful")
                      ]

FAMILIAR_CHOICES = [(1, "Does not match"),
                    (2, "Somewhat does not match"),
                    (3, "Neither matches nor not matches"),
                    (4, "Somewhat matches"),
                    (5, "Perfectly matches")
                    ]


def create_form(form, store):
    initial = {"session_key": store["session_key"],
               "library_name": store["library_name"]}
    form = form(initial=initial)
    if type(form) != Feedback:
        for field in form.declared_fields.keys():
            if type(form.declared_fields[field]) == ChoiceField:
                if store["familiar"]:
                    form.fields[field].choices = FAMILIAR_CHOICES
                    form.declared_fields[field].choices = FAMILIAR_CHOICES
                else:
                    form.fields[field].choices = UNFAMILIAR_CHOICES
                    form.declared_fields[field].choices = UNFAMILIAR_CHOICES
    return form


def initialize_store(session_key, library_name):
    store = dict(library_name=library_name,
                 session_key=session_key,
                 language=None,
                 doc_url=None,
                 general_rating=None,
                 description=None,
                 task_list=None,
                 example_ratios=None,
                 readability_ratios=None,
                 consistency=None,
                 navigability=None,
                 familiar=None,
                 general_form=None,
                 tasks_form=None,
                 method_examples_form=None,
                 class_examples_form=None,
                 text_readability_form=None,
                 code_readability_form=None,
                 consistency_form=None,
                 navigability_form=None,
                 feedback_form=None
                 )
    return store


def update_store(store, values):
    for key, value in values.items():
        store[key] = value
    return store


def create_overview_context(store):
    context = {
        "library_name": store["library_name"],
        "session_key": store["session_key"],
        "language": store["language"],
        "doc_url": store["doc_url"],
        "general_rating": store["general_rating"],
        "description": store["description"],
        "task_list": store["task_list"],
        "example_ratios": store["example_ratios"],
        "readability_ratios": store["readability_ratios"],
        "consistency": store["consistency"],
        "navigability": store["navigability"],
        "familiar": store["familiar"],
        "general_form": GeneralRating(json.loads(store["general_form"])) if store["general_form"] else create_form(GeneralRating, store),
        "tasks_form": TaskList(json.loads(store["tasks_form"])) if store["tasks_form"] else create_form(TaskList, store),
        "method_examples_form": MethodExamples(json.loads(store["method_examples_form"])) if store["method_examples_form"] else create_form(MethodExamples, store),
        "class_examples_form": ClassExamples(json.loads(store["class_examples_form"])) if store["class_examples_form"] else create_form(ClassExamples, store),
        "text_readability_form": TextReadability(json.loads(store["text_readability_form"])) if store["text_readability_form"] else create_form(TextReadability, store),
        "code_readability_form": CodeReadability(json.loads(store["code_readability_form"])) if store["code_readability_form"] else create_form(CodeReadability, store),
        "consistency_form": Consistency(json.loads(store["consistency_form"])) if store["consistency_form"] else create_form(Consistency, store),
        "navigability_form": Navigability(json.loads(store["navigability_form"])) if store["navigability_form"] else create_form(Navigability, store),
        "feedback_form": Feedback(json.loads(store["feedback_form"])) if store["feedback_form"] else create_form(Feedback, store)
    }
    return context
