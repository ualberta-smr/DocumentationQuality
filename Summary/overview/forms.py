from django import forms

from .models import Response


class AnalyzeForm(forms.Form):
    library_name = forms.CharField(required=True)
    language = forms.ChoiceField(
        required=True,
        choices=(
            (None, ""),
            ("Python", "Python"),
            ("Java", "Java"),
            ("Javascript", "Javascript")
        )
    )
    doc_url = forms.CharField(required=True)
    gh_url = forms.CharField(required=False, widget=forms.TextInput(
        attrs={"placeholder": "https://github.com/nltk/nltk.git"}))
    # domain = forms.ChoiceField(
    #     required=True,
    #     choices=(
    #         (None, ""),
    #         ("nlp", "NLP"),
    #         ("json", "JSON"),
    #         ("dom_manipulation", "DOM Manipulation"),
    #         ("http", "HTTP"),
    #         ("''", "Other")
    #     )
    # )


class Demographics(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    years_experience = forms.IntegerField(required=True,
                                          min_value=0,
                                          widget=forms.NumberInput())
    familiar = forms.ChoiceField(
        required=True,
        choices=(
            (None, ""),
            (False, "I am not"),
            (True, "I am")
        )
    )

    class Meta:
        model = Response
        exclude = ("general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class GeneralRating(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    general_rating = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    def clean(self):
        cleaned_data = super(GeneralRating, self).clean()
        general_rating = int(cleaned_data.get("general_rating"))
        if general_rating and general_rating < 0 or general_rating > 5:
            self.add_error("general_rating", "Rating should be between 1 and 5 (inclusive).")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class TaskList(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    task_list = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class MethodExamples(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    code_examples_methods = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class ClassExamples(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    code_examples_classes = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class TextReadability(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    text_readability = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class CodeReadability(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    code_readability = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class Consistency(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    consistency = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class Navigability(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    navigability = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class Feedback(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    usefulness = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
        choices=[(1, "Not useful"),
                 (2, "Somewhat not useful"),
                 (3, "Neither useful nor not useful"),
                 (4, "Somewhat useful"),
                 (5, "Very useful")
                 ]
    )
    would_recommend = forms.ChoiceField(
        required=False,
        choices=(
            (None, ""),
            (True, "I would"),
            (False, "I would not")
        ),
        widget=forms.Select(attrs={"style": "float:left"})
    )
    general_feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"cols": 40, "rows": 4})
    )

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness")
