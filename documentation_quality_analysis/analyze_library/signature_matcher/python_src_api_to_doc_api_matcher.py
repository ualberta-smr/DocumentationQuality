from typing import List, Union

from analyze_library.models.Signature import Signature
import importlib
import inspect
import sys
import subprocess
import pkg_resources

installed_libraries = {pkg.key for pkg in pkg_resources.working_set}


def match_doc_api_to_src_api(library_name: str,
                             mapped_src_apis: dict[str, List[Signature]],
                             doc_apis: List[Union[Signature, None]]) -> tuple[List[Signature], List[Signature]]:
    matched_signatures: List[Signature] = []
    unmatched_signatures: List[Signature] = []

    try:
        for doc_api in doc_apis:
            matched = False

            if doc_api.name in mapped_src_apis:
                same_named_src_api_list = mapped_src_apis[doc_api.name]

                # If name match is one-to-one
                if len(same_named_src_api_list) == 1 and _params_match(src_api=same_named_src_api_list[0],
                                                                       doc_api=doc_api):

                    matched_signatures.append(same_named_src_api_list[0])
                    matched = True

                # If there are multiple source methods with same name
                elif len(same_named_src_api_list) > 1:
                    for src_api in same_named_src_api_list:

                        # If it's a full match
                        if doc_api.fully_qualified_name == src_api.fully_qualified_name and \
                                _params_match(src_api=src_api,
                                              doc_api=doc_api):
                            matched_signatures.append(src_api)
                            matched = True
                            break

                        else:
                            parent_components = doc_api.parent.split('.') if doc_api.parent else []
                            if len(parent_components) > 1:
                                partial_parent = parent_components[-1]

                                partially_qualified_name = '.'.join([partial_parent, doc_api.name])

                                # If it's a partial match
                                if partially_qualified_name == src_api.fully_qualified_name and \
                                        _params_match(src_api=src_api,
                                                      doc_api=doc_api):
                                    matched_signatures.append(src_api)
                                    matched = True
                                    break

                        # If only name matches; has at least one param; and param matches
                        if not matched and (len(doc_api.req_params) + len(doc_api.optional_params)) > 0 \
                                and _params_match(src_api=src_api, doc_api=doc_api):
                            matched_signatures.append(src_api)
                            matched = True
                            break

                        # If lib_name.api_name or file_name.api_name partially matches doc API's fully_qualified_name
                        # and param matches
                        if not matched and src_api.parent is None:
                            # source file name; e.g: x/y/z/file_name.py -> file_name
                            possible_qualified_name_1 = src_api.source.split('/')[-1].split('.')[0] + "." + src_api.name
                            possible_qualified_name_2 = library_name + "." + src_api.name

                            if (possible_qualified_name_1 in doc_api.fully_qualified_name or
                                possible_qualified_name_2 in doc_api.fully_qualified_name) and \
                                    _params_match(src_api=src_api,
                                                  doc_api=doc_api):
                                matched_signatures.append(src_api)
                                matched = True
                                break

            if not matched and doc_api.name:
                unmatched_signatures.append(doc_api)

        unmatched_signatures = _inspect_unmatched_signatures(library_name, unmatched_signatures, doc_apis)
        return matched_signatures, unmatched_signatures

    except Exception as e:
        pass


def _params_match(src_api: Signature, doc_api: Signature) -> bool:
    src_req_params = [param.name for param in src_api.req_params]
    src_opt_params = [param.name for param in src_api.optional_params]

    doc_req_params = [param.name for param in doc_api.req_params]
    doc_opt_params = [param.name for param in doc_api.optional_params]

    if src_req_params.sort() == doc_req_params.sort() and src_opt_params.sort() == doc_opt_params.sort():
        return True

    return False


def _inspect_unmatched_signatures(library_name, unmatched_signatures, doc_apis):
    updated_signatures = unmatched_signatures.copy()
    try:
        required = {library_name.lower()}
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed

        if missing:
            python = sys.executable
            subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

        for api in unmatched_signatures:
            fully_qualified_name = api.fully_qualified_name
            name_components = fully_qualified_name.split('.')
            api_req_params = [param.name for param in api.req_params]
            api_opt_params = [param.name for param in api.optional_params]
            api_params = api_req_params + api_opt_params

            if name_components[-2][0].isupper():
                module_files = '.'.join(name_components[:-2])
                eval_part = "module." + '.'.join(name_components[-2:])
            else:
                module_files = '.'.join(name_components[:-1])
                eval_part = "module." + '.'.join(name_components[-1:])

            try:
                try:
                    module = importlib.import_module(module_files)
                except ModuleNotFoundError as e:
                    components = module_files.split('.')
                    module_files = '.'.join(components[:-1])
                    eval_parts = eval_part.split('.')
                    eval_part = '.'.join([eval_parts[0], components[-1], eval_parts[1]])

                eval_part = eval(eval_part)

                if inspect.isfunction(eval_part) or inspect.isclass(eval_part) or inspect.ismethod(eval_part):
                    params = list(inspect.signature(eval_part).parameters)
                    if 'self' in params:
                        params.remove('self')

                    if params.sort() == api_params.sort():
                        updated_signatures.remove(api)
            except Exception as e:
                pass

    except Exception as e:
        return updated_signatures

    return updated_signatures
