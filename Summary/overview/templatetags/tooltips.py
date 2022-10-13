from django import template

register = template.Library()


@register.simple_tag
def general_rating_tooltip():
    return "This general rating is an equal weighting between all metrics shown below."


@register.simple_tag
def task_list_tooltip():
    return "This list displays the 20 most frequent tasks extracted from the documentation. A green checkmark means a code example exists in the documentation for that task, whereas a red cross means it does not."


@register.simple_tag
def task_list_subheading():
    return "Each link below goes to the section of documentation where the task is found."


@register.simple_tag
def method_examples_tooltip():
    return "This metric indicates how many public API METHODS contain a code example in the documentation."


@register.simple_tag
def class_examples_tooltip():
    return "This metric indicates how many public API CLASSES have at least one class method with a code example in the documentation."


@register.simple_tag
def text_readability_tooltip():
    return "This metric indicates the readability of the text in the documentation based on the ratio of words to sentences and syllables to words."


@register.simple_tag
def code_readability_tooltip():
    return "This metric indicates the readability of the code examples in the documentation based on various code metrics such as the line length, number of identifiers, number of parentheses, etc. Note: This metric currently only works for Java libraries."


@register.simple_tag
def code_readability_caveat_tooltip():
    return "Currently, code readability can only be done on Java libaries."


@register.simple_tag
def consistency_tooltip():
    return "This metric indicates how similar the documentation is with the source code."


@register.simple_tag
def navigability_tooltip():
    return "This metric indicates the navigability (i.e., ease of navigation) of the documentation."

