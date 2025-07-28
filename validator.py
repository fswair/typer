import re
import safelib


pattern = re.compile(
    r'[bfr]*(?:""".*?"""|\'\'\'.*?\'\'\'|"(?:[^"\\\\]|\\\\.)*"|\'(?:[^\'\\\\]|\\\\.)*\')|([a-zA-Z_][a-zA-Z0-9_]*)'
)


def only(iter):
    """
    Filters out empty values from an iterable.

    Args:
        iterable (iterable): The iterable to filter.

    Returns:
        list: A list of non-empty values.
    """
    return set([x for x in iter if x])


def find_names(code: str) -> list[str]:
    """
    Extracts names from the provided code string.

    Args:
        code (str): The code string from which to extract names.

    Returns:
        list[str]: A list of extracted names.
    """
    return pattern.findall(code)


def validate_names(*names, code: str = None) -> str:
    """
    Validates that all names are safe and do not contain any unsafe characters.

    Args:
        *names: Variable number of names to validate.
        code (str, optional): The code string to validate and transform.

    Raises:
        ValueError: If any name is invalid.

    Returns:
        str: The transformed code with entity representations.
    """
    invalid_names = []
    assert names or code, "Must pass names as seperate or code param must passed"
    names = list(names or find_names(code))

    with safelib.Import('typing', 'typing_extensions', raises=False, search_builtins=True) as importer:
        all_types = []
        
        for i, name in enumerate(names):
            if len(sub_names := find_names(name)) > 1:
                all_types.extend(sub_names)
                names.pop(i)
        
        all_types.extend(names)
        
        for name in only(all_types):
            entity = importer.get_entity(name)
            if not importer.valid(entity):
                invalid_names.insert(0, name)

            origin, _ = safelib.state.names[name]
            entity_repr = f'{origin}.{name}' if origin else name
            if code:
                code = re.sub(rf'\b{re.escape(name)}\b', entity_repr, code)

    if invalid_names:
        raise NameError(f"Invalid names found: {', '.join(invalid_names)}")

    return code or True
