import ast
import re
from typing import List

from DocumentationQualityAnalysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from DocumentationQualityAnalysis.analyze_library.models.doc_page import DocPage
from DocumentationQualityAnalysis.analyze_library.models.method_signature import MethodSignature
from DocumentationQualityAnalysis.analyze_library.models.parameter import Parameter


def get_signatures_from_doc(doc_page: DocPage):
    page_url = doc_page.url
    soup = doc_page.content
    dts = soup.find_all("dt")
    method_signatures: List[MethodSignature] = []
    class_signatures = []

    for description in dts:
        desc = []
        for child in description.children:
            if child.name != "a":
                desc.append(child.get_text())

        description = "".join(desc).strip()

        try:
            if "class" in desc:
                class_element = re.findall(re.compile(r'class\s(.*)\(?'), description)
                if len(class_element) > 0:
                    class_signature = _get_parsed_class_details(class_element[0])
                    class_signatures.append(class_signature)
            elif "(" in description:
                code = re.findall('[A-Za-z]*\s(.*\(.*\))', description)
                if len(code) > 0:
                    method = _get_parsed_method_details(method=code[0])
                    method_signatures.append(method)
                else:
                    method = _get_parsed_method_details(method=description)
                    method_signatures.append(method)


        except AttributeError as e:
            print(e)
            print(description)

            # signatures.append([description, page])
    return method_signatures


def _get_parsed_method_details(method: str) -> MethodSignature:
    method_name = ""
    parent = ""
    req_args = []
    opt_args = []
    try:
        method_name, parent = get_ast_parsed_expression(method, method_name, opt_args, parent, req_args)

        method_signature = MethodSignature(name=method_name, parent=parent, req_params=req_args,
                                           optional_params=opt_args, raw_text=method)

        return method_signature

    except:
        return None


def _get_parsed_class_details(class_expr: str) -> ClassConstructorSignature:
    class_name = ""
    parent = ""
    req_args = []
    opt_args = []
    try:
        class_name, parent = get_ast_parsed_expression(class_expr, class_name, opt_args, parent, req_args)

        class_signature = ClassConstructorSignature(name=class_name, parent=parent, req_params=req_args,
                                                    optional_params=opt_args, raw_text=class_expr)

        return class_signature

    except:
        return None


def get_ast_parsed_expression(expression, method_name, opt_args, parent, req_args):
    ast_parsed_method = ast.parse(expression).body[0]
    if type(ast_parsed_method) == ast.Expr:
        if 'value' in ast_parsed_method._fields:
            value = ast_parsed_method.value
            if 'func' in value._fields:
                func = value.func
                if 'attr' in func._fields:
                    method_name = func.attr
                elif 'id' in func._fields:
                    method_name = func.id
                if 'value' in func._fields:
                    if 'id' in func.value._fields:
                        parent = func.value.id
                    elif 'value' in func.value._fields and 'attr' in func.value._fields:
                        parent = func.value.value.id + "." + func.value.attr

            if 'args' in value._fields:
                args = value.args
                for arg in args:
                    if 'id' in arg._fields:
                        param = Parameter(name=arg.id)
                        req_args.append(param)
                    elif 'value' in arg._fields:
                        param = Parameter(name=arg.value.id)
                        opt_args.append(param)
            if 'keywords' in value._fields:
                keywords = value.keywords
                for keyword in keywords:
                    if keyword.arg is None:
                        if 'value' in keyword._fields:
                            param = Parameter(name=keyword.value.id)
                            opt_args.append(param)
                    else:
                        param = Parameter(name=keyword.arg)
                        opt_args.append(param)
    return method_name, parent