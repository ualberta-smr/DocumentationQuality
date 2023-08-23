import ast
import importlib
import logging
import re
import subprocess
import sys
from typing import Dict, List, Union

from DocumentationQualityAnalysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from DocumentationQualityAnalysis.analyze_library.models.matched_function import MatchedFunction
from DocumentationQualityAnalysis.analyze_library.models.method_signature import MethodSignature


def python_match_examples(repo_name: str,
                          examples: List,
                          functions: List[Union[MethodSignature, ClassConstructorSignature, None]]
                          ) -> List[MatchedFunction]:
    method_calls = list()
    var_declarations = dict()

    install(repo_name)
    module = importlib.import_module(repo_name)

    call_regex = re.compile(r"(?:\w+\.)+\w+(?=\()")
    for ex in examples:
        example = ex[0]
        found_calls = re.findall(call_regex, example)
        var_declarations.update(get_declared_variable_mapping(example, {}))
        calls = []
        # Remove duplicate found calls
        [calls.append(item) for item in found_calls if item not in calls]

        for call in calls:
            matched_func = _get_matched_function(call, functions)
            # Check if the function exists in our dictionary
            if not matched_func:
                function_split = call.split(".")
                # If not then maybe it does if we remove the first prefix
                # e.g., nltk.nltk.get -> nltk.get
                if len(function_split) > 1:
                    matched_func = _get_matched_function(function_split[1], functions)
                    if matched_func:
                        # method_calls.add((ex[1], call))
                        method_calls.append(
                            MatchedFunction(method=matched_func, raw_example=example, original_call=call, url=ex[1]))
                    else:
                        if function_split[0] in var_declarations:
                            actual_function = '.'.join([var_declarations[function_split[0]], function_split[1]])
                            matched_func = _get_matched_function(actual_function, functions)
                            if matched_func:
                                # method_calls.add((ex[1], call))
                                method_calls.append(
                                    MatchedFunction(method=matched_func, raw_example=example, original_call=call,
                                                    url=ex[1]))

            elif matched_func:
                # method_calls.add((ex[1], call))
                method_calls.append(
                    MatchedFunction(method=matched_func, raw_example=example, original_call=call, url=ex[1]))

    return method_calls


def _get_matched_function(call: str, functions: List[MethodSignature]) -> Union[MethodSignature, None]:
    for func in functions:
        if func is None:
            continue

        if call == func.fully_qualified_name or call == func.name:
            return func

    return None


def get_declared_variable_mapping(example_code: str, classes: Dict) -> Dict:
    var_declarations = dict()
    func_call_assign_regex = r"(\w+)\s*=\s*(?:\w+\.)+(\w+(?=\())"
    import_regex = r"(?:^\s*(?:import)\s+(\w+(?:\.\w+)*)\s+(?:as)\s+(\w+))|(?:^\s*(?:from)\s+(?:\w+(?:\.\w+)*)\s(?:import)\s+(\w+(?:\.\w+)*)(?:\s+(?:as)\s+(\w+))?)"
    lines = example_code.split('\n')
    for line in lines:
        try:
            line = preprocess_doc_example_line(line)
            if not line:
                continue
            parsed_line = "" if not ast.parse(line.strip()).body else ast.parse(line.strip()).body[0]
            if parsed_line and type(parsed_line) == ast.Import:
                import_values = re.findall(re.compile(import_regex), line)[0]
                import_values = [value for value in import_values if value]
                if len(import_values) == 2:
                    var_declarations[import_values[1]] = import_values[0]

            # elif parsed_line and type(parsed_line) == ast.Assign:
            #     func_call_assign = re.findall(func_call_assign_regex, line)
            #     func_call_assign = func_call_assign[0] if func_call_assign else None
            #
            #     if func_call_assign and len(func_call_assign) == 2 and func_call_assign[1] in classes.keys():
            #         var_declarations[func_call_assign[0]] = func_call_assign[1]

        except Exception as e:
            logging.debug(f"Error in get_declared_variable_mapping. Example code line: \n{line}")
            logging.debug(e)

    return var_declarations


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)


def preprocess_doc_example_line(line: str) -> str:
    jupyter_notebook_prefix = r"(?:^In\s?\[\d+\]\:\s*)|(?:^Out\s?\[\d+\]\:\s*)"
    prompt_regex = r"(?:^>>>\s*)"
    rest_line = r"(.*\S)$"
    code_line = f'(?:{jupyter_notebook_prefix}|{prompt_regex})?{rest_line}'

    processed_line = re.findall(re.compile(code_line), line)
    processed_line = processed_line[0] if len(processed_line) > 0 else ''

    return processed_line
