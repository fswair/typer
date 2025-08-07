import builtins
import re
import typing

import safelib
import typing_extensions
from pydantic import BaseModel

BUILTIN_NAMESPACES = ("builtins", "typing", "typing_extensions")


class ValidationResult(BaseModel):
    """
    Represents the result of a validation operation.
    """

    validated_type: str
    """
    The validated annotation string with type annotations replaced.
    """

    errors: list[Exception] = []
    """
    A list of errors encountered during validation.
    """

    pytype: typing.Any | None = None
    """
    The Python type corresponding to the validated annotation, if available.
    """

    invalid_names: list[str] = []
    """
    A list of names that were found to be invalid during validation.
    """

    type_map: dict[str, str] = {}
    """
    A mapping of type names with their import origin.
    """

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def __bool__(self):
        """
        Returns True if the validation was successful (no invalid names).
        """
        return not self.invalid_names and self.pytype is not None

    @property
    def is_valid(self) -> bool:
        """
        Checks if the validation was successful.

        Returns:
            bool: True if the validation was successful, False otherwise.
        """
        return bool(self)

    def get_origin(self, type_name: str) -> str | None:
        """
        Returns the origin of the type if available.

        Args:
            type_name (str): The name of the type.

        Returns:
            str | None: The origin of the type or None if not found.
        """
        return self.type_map.get(type_name)


class TypeValidator:
    """
    A class for validating and transforming names in code strings.
    """

    def __init__(self, annotation: str):
        assert annotation, "annotation can not be empty"

        self.annotation = annotation
        self.validated_type = annotation
        self.pattern = re.compile(
            r'''[bfr]*(?:""".*?"""|\'\'\'.*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')|(?<!\w)(?<!\.)([a-zA-Z_][a-zA-Z0-9_]*)(?!\.)(?!\w)'''
        )

    def only(self, iter):
        """
        Filters out empty values from an iterable.

        Args:
            iterable (iterable): The iterable to filter.

        Returns:
            list: A list of non-empty values.
        """
        return list(set([x for x in iter if x]))

    def find_names(self, annotation: str = None) -> list[str]:
        """
        Extracts names from the provided code string.

        Args:
            code (str): The code string from which to extract names.

        Returns:
            list[str]: A list of extracted names.
        """
        return self.pattern.findall(annotation or self.annotation)

    def seperate_names(self) -> list[str]:
        """
        Separates names into individual components if they contain multiple names.

        Args:
            names (list[str]): A list of names to separate.

        Returns:
            list[str]: A list of separated names.
        """
        names = self.find_names()
        seperated = []
        for i, name in enumerate(names):
            if len(sub_names := self.find_names(name)) > 1:
                seperated.extend(sub_names)
                names.pop(i)
        seperated.extend(names)
        return self.only(seperated)

    def validate_names(self):
        """
        Validates that all names are safe and do not contain any unsafe characters.

        Args:
            annotation (str, optional): The annotation string to transform.

        Raises:
            ValueError: If any name is invalid.

        Returns:
            tuple: The transformed code/annotation and type information.
        """
        errors = []
        type_map = {}
        invalid_names = []
        all_types = self.seperate_names()

        with safelib.Import(
            "typing", "typing_extensions", raises=False, search_builtins=True
        ) as importer:
            for type_ in all_types:
                if "." in type_ and type_ in BUILTIN_NAMESPACES:
                    continue
                entity = importer.get_entity(type_)
                if not safelib.valid(entity):
                    invalid_names.insert(0, type_)

                entity = safelib.get_entity_info(type_)
                if not entity:
                    continue

                origin, _ = entity
                if origin:
                    entity_repr = f"{origin}.{type_}" if origin else type_
                    print(entity_repr)
                    type_map[type_] = origin
                else:
                    type_map[type_] = ""
                    entity_repr = type_

                self.validated_type = re.sub(
                    rf"(?<!\.)(?<!\w){re.escape(type_)}\b", entity_repr, self.validated_type
                )

            if not invalid_names:
                try:
                    pytype = eval(
                        self.validated_type,
                        {
                            "typing": typing,
                            "typing_extensions": typing_extensions,
                            "builtins": builtins,
                        },
                    )
                except Exception as e:
                    pytype = None
                    errors.append(e)
                return ValidationResult(
                    validated_type=self.validated_type,
                    pytype=pytype,
                    errors=errors,
                    type_map=type_map,
                    invalid_names=invalid_names,
                )
            else:
                return ValidationResult(
                    validated_type=self.validated_type,
                    pytype=None,
                    type_map=type_map,
                    errors=errors,
                    invalid_names=invalid_names,
                )
