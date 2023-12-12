import json

from django.forms import ChoiceField

from doc_quality_analysis_app.forms import Survey


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
                 demographics_form=None,
                 survey_form=None,
                 show_form=False,
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
    show_survey_form, survey_form_success, survey_form = create_survey_form(store)
    context = {
        "library_name": store["library_name"],
        "session_key": store["session_key"],
        "language": store["language"],
        "doc_url": store["doc_url"],
        "gh_url": store["gh_url"],
        "general_rating": int(store["general_rating"]),
        "description": "some description",
        "task_list": None,
        # "method_example_ratios": store["method_example_ratios"],
        # "class_example_ratios": store["class_example_ratios"],
        "example_ratios": store["example_ratios"],
        "readability_ratios": store["readability_ratios"],
        "consistency": store["consistency"],
        "navigability": int(store["navigability"]),
        # "familiar": store["familiar"],
        # "show_demographic_form": store["show_demographic_form"],
        # "show_survey_form": show_survey_form,
        # "survey_form_success": survey_form_success,
        "survey_form": survey_form,
        # "demographics_form": Demographics(json.loads(store["demographics_form"])) if store["demographics_form"] else create_form(Demographics, store),
        # "general_form": GeneralRating(json.loads(store["general_form"])) if store["general_form"] else create_form(GeneralRating, store),
        # "tasks_form": TaskList(json.loads(store["tasks_form"])) if store["tasks_form"] else create_form(TaskList, store),
        # "method_examples_form": MethodExamples(json.loads(store["method_examples_form"])) if store["method_examples_form"] else create_form(MethodExamples, store),
        # "class_examples_form": ClassExamples(json.loads(store["class_examples_form"])) if store["class_examples_form"] else create_form(ClassExamples, store),
        # "text_readability_form": TextReadability(json.loads(store["text_readability_form"])) if store["text_readability_form"] else create_form(TextReadability, store),
        # "code_readability_form": CodeReadability(json.loads(store["code_readability_form"])) if store["code_readability_form"] else create_form(CodeReadability, store),
        # "consistency_form": Consistency(json.loads(store["consistency_form"])) if store["consistency_form"] else create_form(Consistency, store),
        # "navigability_form": Navigability(json.loads(store["navigability_form"])) if store["navigability_form"] else create_form(Navigability, store),
        # "feedback_form": Feedback(json.loads(store["feedback_form"])) if store["feedback_form"] else create_form(Feedback, store)
    }
    return context


def create_survey_form(store):
    show_survey_form = False
    form_success = True
    if store["survey_form"]:
        data = json.loads(store["survey_form"])
        form = Survey(data)
        show_survey_form = True
        if store["familiar"]:
            if len(form.errors) > 1:
                form_success = False
        elif len(form.errors) > 2:
            form_success = False
    else:
        data = dict(session_key=store["session_key"],
                    library_name=store["library_name"])
        form = Survey(initial=data)
        excluded = ["usefulness", "where_see", "matching"]
        for field in form.declared_fields.keys():
            if field not in excluded:
                if type(form.declared_fields[field]) == ChoiceField:
                    # if store["familiar"]:
                    #     form.fields[field].choices = FAMILIAR_CHOICES
                    #     form.declared_fields[field].choices = FAMILIAR_CHOICES
                    # else:
                    form.fields[field].choices = UNFAMILIAR_CHOICES
                    form.declared_fields[field].choices = UNFAMILIAR_CHOICES
    return show_survey_form, form_success, form


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

