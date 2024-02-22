from django import forms

from doc_quality_analysis_app.models import Response


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
    gh_url = forms.CharField(required=True, widget=forms.TextInput(
        attrs={"placeholder": "https://github.com/nltk/nltk.git"}))


class Survey(forms.ModelForm):
    session_key = forms.CharField(widget=forms.HiddenInput())
    library_name = forms.CharField(widget=forms.HiddenInput())
    general_rating = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
    task_list = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
    code_examples_methods = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
    code_examples_classes = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
    text_readability = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
    code_readability = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
    consistency = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
    navigability = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"})
    )
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
    where_see = forms.ChoiceField(
        required=False,
        choices=(
            (None, ""),
            ("readme", "README file badge"),
            ("package_manager", "Package manager"),
            ("other", "Other")
        ),
        widget=forms.Select(attrs={"style": "float:left"})
    )
    matching = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={"class": "form-check-inline"}),
        choices=[(1, "Strongly disagree"),
                 (2, "Disagree"),
                 (3, "Neither agree nor disagree"),
                 (4, "Somewhat agree"),
                 (5, "Strongly agree")
                 ]
    )
    general_feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"cols": 40, "rows": 4})
    )

    def clean(self):
        cleaned_data = super(Survey, self).clean()
        errors = []
        for key in cleaned_data.keys():
            if key != "general_feedback":
                if not cleaned_data[key] or cleaned_data[key] == "None":
                    if key == "general_rating":
                        errors.append((key, "Please rate the General rating."))
                    elif key == "task_list":
                        errors.append((key, "Please rate the Documented library tasks."))
                    elif key == "code_examples_methods":
                        errors.append((key, "Please rate the Methods with code examples."))
                    elif key == "code_examples_classes":
                        errors.append((key, "Please rate the Classes with code examples. "))
                    elif key == "text_readability":
                        errors.append((key, "Please rate the Readability of text."))
                    elif key == "code_readability":
                        errors.append((key, "Please rate the Readability of code examples."))
                    elif key == "consistency":
                        errors.append((key, "Please rate the Documentation/Source code similarity."))
                    elif key == "navigability":
                        errors.append((key, "Please rate the Navigation rating."))
                    elif key == "usefulness":
                        errors.append((key, "Please rate the Usefulness of the summary."))
                    elif key == "where_see":
                        errors.append((key, "Please state where you would like to see this summary."))
                    elif key == "matching":
                        errors.append((key, "Please rate the how much the documentation matches with your experience."))
        for error, error_message in errors:
            self.add_error(error, error_message)
        return cleaned_data

    class Meta:
        model = Response
        exclude = ("years_experience",
                   "familiar")

