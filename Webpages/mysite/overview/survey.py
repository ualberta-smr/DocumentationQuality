from django import forms
from .models import Response


class Demographics(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    years_experience = forms.IntegerField(widget=forms.NumberInput())
    used_before = forms.ChoiceField(
        required=True,
        choices=((True, "I have"), (False, "I have not"))
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
        widget=forms.Textarea()
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
    class Meta:
        model = Response
        exclude = ("session_key",
                   "library_name",
                   "years_experience",
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


class CodeExamples(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = Response
        exclude = ("years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class Readability(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = Response
        exclude = ("session_key",
                   "library_name",
                   "years_experience",
                   "used_before",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "consistency",
                   "navigability",
                   "usefulness",
                   "would_recommend",
                   "general_feedback")


class Consistency(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = Response
        exclude = ("session_key",
                   "library_name",
                   "years_experience",
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
    class Meta:
        model = Response
        exclude = ("session_key",
                   "library_name",
                   "years_experience",
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
    class Meta:
        model = Response
        exclude = ("session_key",
                   "library_name",
                   "years_experience",
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