from django import template

register = template.Library()


@register.simple_tag
def general_rating_tooltip():
    return "This general rating is an equal weighting between all metrics shown below."


@register.simple_tag
def task_list_tooltip():
    return "This list displays the 20 most frequent tasks extracted from the documentation. The green checkmarks means a code example exists for that task in the documentation, whereas a red cross means it does not."


@register.simple_tag
def method_examples_tooltip():
    return "This metric indicates how many public API METHODS contain a code example in the documentation."


@register.simple_tag
def class_examples_tooltip():
    return "This metric indicates how many public API CLASSES contain a code example in the documentation."


@register.simple_tag
def text_readability_tooltip():
    return "This metric indicates the readability of the text in the documentation based on the Flesch Reading Ease metric."


@register.simple_tag
def code_readability_tooltip():
    return "This metric indicates the readability of the code examples in the documentation based on Scalabrino et al. (JSEP 2018). Note: This metric currently only works for Java libraries."


@register.simple_tag
def code_readability_caveat_tooltip():
    return "Currently, code readability can only be done on Java libaries."


@register.simple_tag
def consistency_tooltip():
    return "This metric indicates how similar the documentation is with the source code."


@register.simple_tag
def navigability_tooltip():
    return "This metric indicates the navigability (i.e., ease of navigation) of the documentation."

