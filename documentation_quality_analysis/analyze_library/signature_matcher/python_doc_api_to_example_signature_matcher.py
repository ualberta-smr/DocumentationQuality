import ast
import logging
import re
import subprocess
import sys
from typing import Dict, List, Union

from analyze_library.models.Signature import Signature
from analyze_library.models.class_constructor_signature import ClassConstructorSignature
from analyze_library.models.doc_code_example import DocCodeExample
from analyze_library.models.matched_call import MatchedCall


def match_examples_to_doc_api(repo_name: str,
                              examples: List[DocCodeExample],
                              doc_apis: List[Union[Signature, None]]
                              ) -> List[MatchedCall]:
    matched_apis = list()
    var_declarations = dict()
    classes: List[ClassConstructorSignature | None] = [x for x in doc_apis if type(x) == ClassConstructorSignature]

    call_regex = re.compile(r"(?:\w+\.)*\w+(?=\()")
    for ex in examples:
        example = ex.example
        found_calls = re.findall(call_regex, example)
        var_declarations.update(_get_declared_variable_mapping(example, classes))
        calls = []
        # Remove duplicate found calls
        [calls.append(item) for item in found_calls if item not in calls]

        for call in calls:
            matched_call = _get_matched_function(call, doc_apis)
            # Check if the function exists in our dictionary
            if not matched_call:
                statement_parts = call.split(".")
                variable = statement_parts[0]

                if variable in var_declarations:
                    while variable in var_declarations:
                        if variable == var_declarations[variable]:
                            break
                        variable = var_declarations[variable]

                    statement_parts[0] = variable
                    actual_function = '.'.join(statement_parts)

                    matched_func = _get_matched_function(actual_function, doc_apis)
                    if matched_func:
                        matched_apis.append(
                            MatchedCall(called_signature=matched_func,
                                        raw_example=ex,
                                        original_call=call,
                                        url=ex.url))
                elif len(statement_parts) > 1:
                    # If not then maybe it does if we remove the first prefix
                    # e.g., nltk.nltk.get -> nltk.get
                    first_term_removed_function = '.'.join(statement_parts[1:])
                    matched_call = _get_matched_function(call=first_term_removed_function,
                                                         functions=doc_apis,
                                                         no_partial_match=True)
                    if matched_call:
                        matched_apis.append(
                            MatchedCall(called_signature=matched_call,
                                        raw_example=ex,
                                        original_call=call,
                                        url=ex.url))

            elif matched_call:
                matched_apis.append(
                    MatchedCall(called_signature=matched_call, raw_example=ex, original_call=call, url=ex.url))

    return matched_apis


def _get_matched_function(call: str, functions: List[Signature], no_partial_match=False) -> Union[Signature, None]:
    for func in functions:
        if func is None:
            continue

        if call == func.fully_qualified_name:
            return func

        elif not no_partial_match:
            parents = func.parent.split(".") if func.parent else []
            if len(parents) > 1:
                partial_terms = parents[1:]
                partial_terms.extend([func.name])
                partial_qualified_name = ".".join(partial_terms)
                if call == partial_qualified_name:
                    return func

        if type(func) == ClassConstructorSignature:
            if call == func.name:
                return func

    if len(call.split('.')) == 1:
        same_named_methods = [x for x in functions if x.name == call]
        if len(same_named_methods) == 1:
            return same_named_methods[0]

    return None


def _get_declared_variable_mapping(example_code: str, classes: List[ClassConstructorSignature]) -> Dict:
    var_declarations = dict()
    func_call_assign_regex = r"(\w+)\s*=\s*((?:\w+\.)*(\w+(?=\()))"
    import_regex = r"(?:^\s*(?:import)\s+(\w+(?:\.\w+)*)\s+(?:as)\s+(\w+))|(?:^\s*(?:from)\s+(?:\w+(?:\.\w+)*)\s(?:import)\s+(\w+(?:\.\w+)*)(?:\s+(?:as)\s+(\w+))?)"
    lines = example_code.split('\n')
    for line in lines:
        try:
            line = _preprocess_doc_example_line(line)
            line = _remove_open_brackets(line)
            if not line:
                continue
            parsed_line = "" if not ast.parse(line.strip()).body else ast.parse(line.strip()).body[0]
            if parsed_line and type(parsed_line) == ast.Import:
                import_values = re.findall(re.compile(import_regex), line)[0]
                import_values = [value for value in import_values if value]
                if len(import_values) == 2:
                    var_declarations[import_values[1]] = import_values[0]

            elif parsed_line and type(parsed_line) == ast.ImportFrom:
                import_module = parsed_line.module
                for name in parsed_line.names:
                    imported_value_name = name.name
                    full_value = '.'.join([import_module, imported_value_name])
                    var_declarations[imported_value_name] = full_value

                # if len(import_values) == 2:
                #     var_declarations[import_values[1]] = import_values[0]

            elif parsed_line and type(parsed_line) == ast.Assign:
                matched_list = re.findall(func_call_assign_regex, line)
                func_call_assign = matched_list[0] if matched_list else None

                if func_call_assign and len(func_call_assign) >= 2:
                    called_class = [x for x in classes if x.name == func_call_assign[-1]]
                    if called_class:
                        var_declarations[func_call_assign[0]] = func_call_assign[-1]

        except Exception as e:
            logging.debug(f"Error in get_declared_variable_mapping. Example code line: \n{line}")
            logging.debug(e)

    return var_declarations


def _install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)


def _preprocess_doc_example_line(line: str) -> str:
    jupyter_notebook_prefix = r"(?:^In\s?\[\d+\]\:\s*)|(?:^Out\s?\[\d+\]\:\s*)"
    prompt_regex = r"(?:^>>>\s*)"
    rest_line = r"(.*\S)$"
    code_line = f'(?:{jupyter_notebook_prefix}|{prompt_regex})?{rest_line}'

    processed_line = re.findall(re.compile(code_line), line)
    processed_line = processed_line[0] if len(processed_line) > 0 else ''

    return processed_line


def _remove_open_brackets(line: str) -> str:
    if line.count('(') == line.count(')'):
        return line

    first_bracket_occurrence = line.find('(')
    line = line[0:first_bracket_occurrence + 1] + ')'

    return line
