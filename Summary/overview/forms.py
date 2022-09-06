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
            ("Javascript", "Javascript"),
            ("", "Other")
        )
    )
    doc_url = forms.CharField(required=True)
    gh_url = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "https://github.com/nltk/nltk.git"}))
    domain = forms.ChoiceField(
        required=True,
        choices=(
            (None, ""),
            ("nlp", "NLP"),
            ("json", "JSON"),
            ("dom_manipulation", "DOM Manipulation"),
            ("http", "HTTP"),
            ("''", "Other")
        )
    )


class Demographics(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    years_experience = forms.IntegerField(required=True, min_value=0, widget=forms.NumberInput())
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
    general_rating = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
    )

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
    task_list = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
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
    code_examples_methods = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
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
    code_examples_classes = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
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
    text_readability = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
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
    code_readability = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
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
    consistency = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
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
    navigability = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
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
    usefulness = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 50})
    )
    would_recommend = forms.ChoiceField(
        required=True,
        choices=(
            (None, ""),
            (True, "I would"),
            (False, "I would not")
        )
    )
    general_feedback = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 50})
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
