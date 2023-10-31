import ast
import re
from typing import List, Union

from analyze_library.models.Signature import Signature
from analyze_library.models.class_constructor_signature import ClassConstructorSignature
from analyze_library.models.doc_page import DocPage
from analyze_library.models.method_signature import MethodSignature
from analyze_library.models.parameter import Parameter

REQ_STATEMENT_TYPES = ['method', 'class', 'function', 'exception']
PARSE_GENERATED_HTML = "PARSE_GENERATED_HTML"
PARSE_ANY_DOC = "PARSE_ANY_DOC"


def get_signatures_from_doc(doc_page: DocPage) -> List[Signature]:
    soup = doc_page.content
    signatures: List[Signature] = []

    dt_tags = soup.find_all("dt")

    if dt_tags:
        parsing_method = PARSE_GENERATED_HTML
        signatures.extend(get_signature_from_generated_html(doc_page))

    else:
        parsing_method = PARSE_ANY_DOC
        signatures.extend(get_signatures_from_section(doc_page))

    return signatures


def get_signature_from_generated_html(doc_page: DocPage) -> List[Signature]:
    soup = doc_page.content
    url = doc_page.url
    tags = soup.find_all("dt")

    signatures: List[Signature] = []

    for tag in tags:
        desc = []

        for child in tag.children:
            if child.name != "a":
                desc.append(child.get_text())

        description = "".join(desc).strip()

        try:
            _append_signature_from_generated_html_tag(description, signatures, tag, url)

        except AttributeError as e:
            print(e)
            print(description)

    return signatures


def get_signatures_from_section(doc_page: DocPage) -> List[Signature]:
    soup = doc_page.content
    url = doc_page.url
    signatures: List[Signature] = []

    tags = soup.find_all("code")

    for tag in tags:
        desc = []
        last_component = ''
        id_components = []

        if tag.parent.name == "pre":
            continue

        parent_ids = [p.get('id') for p in tag.parents if p.get('id')]
        if len(parent_ids) > 0:
            parent_id = parent_ids[0]
            id_components = parent_id.split('.')
            last_component: str = id_components[-1]

        for child in tag.children:
            if child.name != "a":
                desc.append(child.get_text())

        description = "".join(desc).strip()

        try:
            if last_component in description:
                parent = '.'.join(id_components[0:-1])
                _append_signature_from_statement(description, signatures, url, parent)

        except AttributeError as e:
            print(e)
            print(description)

    return signatures


def _append_signature_from_statement(description, signatures, source, parent):
    if "class" in description:
        class_element = re.findall(re.compile(r'class\s(.*)'), description)
        if len(class_element) > 0:
            class_signature: ClassConstructorSignature = _get_parsed_class_details(class_element[0], source=source)
            if class_signature:
                signatures.append(class_signature)
    elif "(" in description:
        code = re.findall('([^\s]+\(.*\))', description)

        if len(code) > 0:
            method = _get_parsed_method_details(method=code[0], source=source, parent=parent)
            if method:
                signatures.append(method)
        else:
            method = _get_parsed_method_details(method=description, source=source, parent=parent)
            if method:
                signatures.append(method)


def _append_signature_from_generated_html_tag(description, signatures, tag, url):
    if 'id' in tag.attrs:
        statement_type = tag.parent.attrs['class'][-1]

        if statement_type in REQ_STATEMENT_TYPES:
            name = tag.attrs['id']
            name_components = name.split('.')
            last_component: str = name_components[-1]
            parent = '.'.join(name_components[0:-1])

            if last_component[0].isupper():
                class_element = re.findall(r'(?:class\s|final class\s|exception\s)?(.+)', description)[0]
                class_signature: ClassConstructorSignature = _get_parsed_class_details(
                    class_expr=class_element,
                    source=url,
                    parent=parent)
                if class_signature:
                    signatures.append(class_signature)
                else:
                    missed_signature = ClassConstructorSignature(name='', parent='', source=url, raw_text=class_element)
                    signatures.append(missed_signature)

            elif last_component[0].islower() or last_component[0] == "_":
                method = re.findall(r'(?:method\s|classmethod\s)?(.+)', description)[0]
                method_signature = _get_parsed_method_details(
                    method=method,
                    source=url,
                    parent=parent)
                if method_signature:
                    signatures.append(method_signature)
                else:
                    missed_signature = MethodSignature(name='', parent='', source=url, raw_text=method)
                    signatures.append(missed_signature)


def _get_parsed_method_details(method: str, source: str, parent: Union[str, None] = None) \
        -> Union[MethodSignature, None]:
    method_name = ""
    parent = parent
    req_args = []
    opt_args = []
    try:
        method = _remove_special_param(statement=method)

        method_name, parent = get_ast_parsed_expression(method, method_name, opt_args, parent, req_args)

        method_signature = MethodSignature(name=method_name, parent=parent, req_params=req_args,
                                           optional_params=opt_args, raw_text=method, source=source)

        return method_signature

    except:
        return None


def _remove_special_param(statement):
    # e.g: asterisk_usage(either, *, keyword_only) or slash_usage(positional_only, /, either)
    mid_special_params = re.findall('[(].*(, ?[*|/] ?,)', statement)

    # e.g: Series.fill(*, axis=None, inplace=False, limit=None)
    side_special_params = re.findall('[(]( ?\* ?,)|[(].*(, ?/) ?[)]', statement)

    if mid_special_params:
        statement = statement.replace(mid_special_params[0], ',')

    elif side_special_params:
        if side_special_params[0][0]:
            statement = statement.replace(side_special_params[0][0], '')
        elif side_special_params[0][1]:
            statement = statement.replace(side_special_params[0][1], '')

    return statement


def _get_parsed_class_details(class_expr: str, source: str, parent: Union[str, None] = "") \
        -> Union[ClassConstructorSignature, None]:
    class_name = ""
    parent = parent
    req_args = []
    opt_args = []
    raw_text = class_expr

    try:
        if not "(" in class_expr and not ")" in class_expr:
            class_expr = class_expr.strip() + "()"

        class_expr = _remove_special_param(statement=class_expr)

        class_name, parent = get_ast_parsed_expression(class_expr, class_name, opt_args, parent, req_args)

        class_signature = ClassConstructorSignature(name=class_name, parent=parent, req_params=req_args,
                                                    optional_params=opt_args, raw_text=raw_text, source=source)

        return class_signature

    except:
        return None


def _remove_special_param(statement):
    # e.g: asterisk_usage(either, *, keyword_only) or slash_usage(positional_only, /, either)
    mid_special_params = re.findall('[(].*(, ?[\*|\/] ?,)', statement)

    # e.g: Series.fill(*, axis=None, inplace=False, limit=None)
    side_special_params = re.findall('[(]( ?\* ?,)|[(].*(, ?\/) ?[)]', statement)

    if mid_special_params:
        statement = statement.replace(mid_special_params[0], ',')

    elif side_special_params:
        if side_special_params[0][0]:
            statement = statement.replace(side_special_params[0][0], '')
        elif side_special_params[0][1]:
            statement = statement.replace(side_special_params[0][1], '')

    return statement


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
                if not parent and 'value' in func._fields:
                    if 'id' in func.value._fields:
                        parent = func.value.id
                    elif 'value' in func.value._fields and 'attr' in func.value._fields:
                        parent = ".".join([func.value.value.id, func.value.attr])

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
