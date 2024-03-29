from django import template

register = template.Library()


@register.simple_tag
def demographics_years_experience(qn):
    return str(qn) + ". How many years of software development experience do you have?\n(Not just with this library)"


@register.simple_tag
def general_rating_familiar(qn):
    return str(qn) + ". How does the general rating match your intuition with the general quality of the library's documentation?"


@register.simple_tag
def task_list_familiar(qn):
    return str(qn) + ". How much does the list of documented tasks match your intuition of the tasks supported by the library?"


@register.simple_tag
def method_examples_familiar(qn):
    return str(qn) + ". How much does the rating of methods with code examples match your intuition of methods with code examples in the documentation?"


@register.simple_tag
def class_examples_familiar(qn):
    return str(qn) + ". How much does the rating of classes with a code example match your intuition of classes with a code example in the documentation?"


@register.simple_tag
def text_readability_familiar(qn):
    return str(qn) + ". How much does the rating of text readability match your intuition of the documentation's text readability?"


@register.simple_tag
def code_readability_familiar(qn):
    return str(qn) + ". How much does the rating for code example readability match your intuition of the documentation's code example readability"


@register.simple_tag
def consistency_familiar(qn):
    return str(qn) + ". How much does the rating of similarity between the documentation and source code match your intuition of the documentation/source code similarity?"


@register.simple_tag
def navigability_familiar(qn):
    return str(qn) + ". How much does the rating of navigability match your intuition of the documentation's navigability?"


@register.simple_tag
def general_rating_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a general rating of " + str(library_name) + " documentation's quality?"


@register.simple_tag
def task_list_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a list of documented library tasks found for " + str(library_name) + "'s documentation?"


@register.simple_tag
def method_examples_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a rating of methods with a code example for " + str(library_name) + "'s documentation?"


@register.simple_tag
def class_examples_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a rating of classes with a code example for " + str(library_name) + "'s documentation?"


@register.simple_tag
def text_readability_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a rating of readability of text for " + str(library_name) + "'s documentation?"


@register.simple_tag
def code_readability_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a rating of readability of code examples for " + str(library_name) + "'s documentation?"


@register.simple_tag
def consistency_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a rating of similarity between " + str(library_name) + "'s source code and documentation?"


@register.simple_tag
def navigability_not_familiar(qn, library_name):
    return str(qn) + ". How useful is having a rating of navigability for " + str(library_name) + "'s documentation?"


@register.simple_tag
def general_useful(qn, library_name):
    return str(qn) + ". How useful is having a summary of " + str(library_name) + "'s documentation quality?"


@register.simple_tag
def where_see(qn):
    return str(qn) + ". Where would you like to see this documentation quality summary?"


@register.simple_tag
def matching(qn, library_name):
    return str(qn) + ". To what extent do you agree or disagree with this statement: The documentation quality metrics represented in this summary are consistent with my experience working with " + str(library_name) + " (e.g., the metrics indicate low documentation quality and your experience is that this library is poorly documented, or vice versa)."


@register.simple_tag
def additional_feedback(qn, library_name):
    return str(qn) + ". Please provide any additional feedback you have about " + str(library_name) + "'s documentation quality summary."
