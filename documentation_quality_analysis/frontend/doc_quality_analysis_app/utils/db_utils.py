from doc_quality_analysis_app.models import Library


def get_library(library_name: str) -> Library:
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
