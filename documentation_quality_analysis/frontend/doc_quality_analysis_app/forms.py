from django import forms


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
