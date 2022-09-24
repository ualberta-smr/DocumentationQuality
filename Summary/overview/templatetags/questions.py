from django import template

register = template.Library()


@register.simple_tag
def general_rating_familiar():
    return "How does the general rating match your intuition with the general quality of the library's documentation?"


@register.simple_tag
def task_list_familiar():
    return "How much does the list of documented tasks match your intuition of the tasks supported by the library?"


@register.simple_tag
def method_examples_familiar():
    return "How much does the rating of methods with code examples match your intuition of methods with code examples in the documentation?"


@register.simple_tag
def class_examples_familiar():
    return "How much does the rating of classes with a code example match your intuition of classes with a code example in the documentation?"


@register.simple_tag
def text_readability_familiar():
    return "How much does the rating of text readability match your intuition of the documentation's text readability?"


@register.simple_tag
def code_readability_familiar():
    return "How much does the rating for code example readability match your intuition of the documentation's code example readability"


@register.simple_tag
def consistency_familiar():
    return "How much does the rating of similarity between the documentation and source code match your intuition of the documentation/source code similarity?"


@register.simple_tag
def navigability_familiar():
    return "How much does the rating of navigability match your intuition of the documentation's navigability?"


@register.simple_tag
def general_rating_not_familiar():
    return "How useful is having a general rating of the library documentation's quality?"


@register.simple_tag
def task_list_not_familiar():
    return "How useful is having a list of documented library tasks found in the documentation?"


@register.simple_tag
def method_examples_not_familiar():
    return "How useful is having a rating of methods with a code example in the documentation?"


@register.simple_tag
def class_examples_not_familiar():
    return "How useful is having a rating of classes with a code example in the documentation?"


@register.simple_tag
def text_readability_not_familiar():
    return "How useful is having a rating of readability of text in the documentation?"


@register.simple_tag
def code_readability_not_familiar():
    return "How useful is having a rating of readability of code examples in the documentation?"


@register.simple_tag
def consistency_not_familiar():
    return "How useful is having a rating of similarity between the source code and documentation?"


@register.simple_tag
def navigability_not_familiar():
    return "How useful is having a rating of navigability of the documentation?"


@register.simple_tag
def general_useful():
    return "How useful is having a documentation quality summary of a library's documentation?"


@register.simple_tag
def would_recommend():
    return "Would you recommend this documentation quality summary tool to others?"


@register.simple_tag
def additional_feedback():
    return "Please provide any additional feedback you have about this documentation quality summary."
