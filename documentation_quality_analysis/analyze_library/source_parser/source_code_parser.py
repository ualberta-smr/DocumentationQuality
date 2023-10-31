import ast
import re
from typing import List

from analyze_library.models.Signature import Signature
from analyze_library.models.class_constructor_signature import ClassConstructorSignature
from analyze_library.models.method_signature import MethodSignature
from analyze_library.models.parameter import Parameter
from analyze_library.source_parser.source_util import get_source_files

LANGUAGE = 'python'


def get_methods_and_classes_from_source_code(repo_name: str, repo_path: str) -> dict[str, List[Signature]]:
    mapped_signatures: dict[str, List[Signature]] = {}

    if repo_path is None:
        return mapped_signatures

    source_files = get_source_files(repo_name, repo_path)

    for source_file in source_files:
        mapped_signatures = _get_python_signatures(repo_name, source_file, mapped_signatures)

    return mapped_signatures


def _get_python_signatures(repo_name: str, source_file: str, mapped_signatures: dict[str, List[Signature]]
                           ) -> dict[str, List[Signature]]:
    api_source = '/'.join(source_file.split('/')[1:])
    repo_name = repo_name.lower()

    with open(source_file, "r", encoding="utf-8") as f:
        try:
            a = ast.parse(f.read(), mode="exec")
            private_function = re.compile("^_(?!_)")

            for file_item in a.body:

                if type(file_item) is ast.ClassDef:

                    class_name = file_item.name
                    if class_name == "Value":
                        print('here')
                    constructor_found = False

                    for class_item in file_item.body:

                        if type(class_item) is ast.FunctionDef:
                            if class_item.name == "__init__":
                                constructor_found = True
                                func_name, required, optionals = _extract_python_ast_args(class_item)
                                class_signature = ClassConstructorSignature(name=class_name,
                                                                            parent='',
                                                                            req_params=required,
                                                                            optional_params=optionals,
                                                                            source=api_source)

                                mapped_signatures = _add_signature_to_map(mapped_signatures, class_signature)

                            # We ignore methods that start with "_" because they are
                            # typically considered private methods
                            elif not re.match(private_function, class_item.name):
                                func_name, required, optionals = _extract_python_ast_args(class_item)
                                func_signature = MethodSignature(name=func_name,
                                                                 parent=class_name,
                                                                 req_params=required,
                                                                 optional_params=optionals,
                                                                 source=api_source)

                                mapped_signatures = _add_signature_to_map(mapped_signatures, func_signature)
                    if not constructor_found:
                        class_signature = ClassConstructorSignature(name=class_name,
                                                                    parent=None,
                                                                    source=api_source)

                        mapped_signatures = _add_signature_to_map(mapped_signatures, class_signature)

                elif type(file_item) is ast.FunctionDef:

                    if not re.match(private_function, file_item.name):
                        func_name, required, optionals = _extract_python_ast_args(file_item)
                        func_signature = MethodSignature(
                            name=func_name,
                            parent=None,
                            req_params=required,
                            optional_params=optionals,
                            source=api_source)

                        mapped_signatures = _add_signature_to_map(mapped_signatures, func_signature)
        except Exception as e:
            pass

    return mapped_signatures


def _extract_python_ast_args(func_def):
    params = func_def.args.args
    defaults = func_def.args.defaults

    params.reverse()
    defaults.reverse()

    optionals = []
    # Find all the optional arguments
    for args in zip(params, defaults):
        optionals.append(Parameter(name=args[0].arg))
    # Find the required arguments
    required = []
    for arg in params:
        found = False
        for optional in optionals:
            if arg.arg == optional.name:
                found = True
                break
        if not found and not arg.arg == "self":
            required.append(Parameter(name=arg.arg))
    if func_def.args.kwarg:
        optionals.append(Parameter(name=func_def.args.kwarg.arg))

    return func_def.name, required, optionals


def _add_signature_to_map(mapped_signatures: dict[str, List[Signature]],
                          signature: Signature) -> dict[str, List[Signature]]:
    name = signature.name

    if name in mapped_signatures:
        mapped_signatures[name].append(signature)
    else:
        mapped_signatures[name] = [signature]

    return mapped_signatures
