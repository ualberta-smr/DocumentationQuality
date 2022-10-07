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
    years_experience = forms.IntegerField(required=False,
                                          min_value=0,
                                          widget=forms.NumberInput(attrs={
                                              "style": "width:100px;text-align:right;"}))
    familiar = forms.ChoiceField(
        required=False,
        choices=(
            (None, ""),
            (False, "I am not"),
            (True, "I am")
        )
    )

    def clean(self):
        cleaned_data = super(Demographics, self).clean()
        if "years_experience" in cleaned_data:
            years_experience = cleaned_data.get("years_experience")
            if years_experience is None or int(years_experience) < 0:
                self.add_error("years_experience",
                               "Years of experience should be at least 0.")
        if "familiar" in cleaned_data:
            familiar = (cleaned_data.get("familiar"))
            if not familiar:
                self.add_error("familiar",
                               "Please state whether you are or are not familiar with the library.")
        return cleaned_data

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
        general_rating = cleaned_data.get("general_rating")
        if not general_rating or int(general_rating) < 0 or int(
                general_rating) > 5:
            self.add_error("general_rating", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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

    def clean(self):
        cleaned_data = super(TaskList, self).clean()
        task_list = cleaned_data.get("task_list")
        if not task_list or int(task_list) < 0 or int(task_list) > 5:
            self.add_error("task_list", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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

    def clean(self):
        cleaned_data = super(MethodExamples, self).clean()
        code_examples_methods = cleaned_data.get("code_examples_methods")
        if not code_examples_methods or int(code_examples_methods) < 0 or int(
                code_examples_methods) > 5:
            self.add_error("code_examples_methods", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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

    def clean(self):
        cleaned_data = super(ClassExamples, self).clean()
        code_examples_classes = cleaned_data.get("code_examples_classes")
        if not code_examples_classes or int(code_examples_classes) < 0 or int(
                code_examples_classes) > 5:
            self.add_error("code_examples_classes", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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

    def clean(self):
        cleaned_data = super(TextReadability, self).clean()
        text_readability = cleaned_data.get("text_readability")
        if not text_readability or int(text_readability) < 0 or int(
                text_readability) > 5:
            self.add_error("text_readability", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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

    def clean(self):
        cleaned_data = super(CodeReadability, self).clean()
        code_readability = cleaned_data.get("code_readability")
        if not code_readability or int(code_readability) < 0 or int(
                code_readability) > 5:
            self.add_error("code_readability", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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

    def clean(self):
        cleaned_data = super(Consistency, self).clean()
        consistency = cleaned_data.get("consistency")
        if not consistency or int(consistency) < 0 or int(consistency) > 5:
            self.add_error("consistency", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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

    def clean(self):
        cleaned_data = super(Navigability, self).clean()
        navigability = cleaned_data.get("navigability")
        if not navigability or int(navigability) < 0 or int(navigability) > 5:
            self.add_error("navigability", "Please select a rating.")
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
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
        required=False,
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

    def clean(self):
        cleaned_data = super(Feedback, self).clean()
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar",
                   "general_rating",
                   "task_list",
                   "code_examples_methods",
                   "code_examples_classes",
                   "text_readability",
                   "code_readability",
                   "consistency",
                   "navigability",
                   "usefulness")
