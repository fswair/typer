# Type Validator

A robust Python library for validating and transforming type annotations with comprehensive safety checks and automatic import resolution.

## Features

- **Type Annotation Validation**: Validates Python type annotations for safety and correctness
- **Automatic Import Resolution**: Automatically resolves and adds proper module prefixes to type names
- **Safety Checks**: Uses `safelib` to ensure all types are safe to use
- **Comprehensive Error Handling**: Provides detailed error reporting and validation results
- **Support for Complex Types**: Handles Union types, Generics, Callables, and more

## Installation

```bash
pip install -U safelib pydantic typing_extensions
```

## Quick Start

```python
from validator import TypeValidator

# Validate a simple type annotation
validator = TypeValidator('Union[Callable[[], int], int]')
result = validator.validate_names()

print(result.validated_type)
# Output: typing.Union[typing.Callable[[], builtins.int], builtins.int]

print(result.pytype)
# Output: typing.Union[typing.Callable[[], int], int]

print(result.is_valid)
# Output: True
```

## API Reference

### TypeValidator

The main class for validating type annotations.

#### Constructor

```python
TypeValidator(annotation: str)
```

**Parameters:**
- `annotation` (str): The type annotation string to validate

#### Methods

##### `validate_names() -> ValidationResult`

Validates all type names in the annotation and returns a comprehensive result.

**Returns:**
- `ValidationResult`: A detailed result object containing validation information

##### `find_names(annotation: str = None) -> list[str]`

Extracts all type names from the annotation string.

**Parameters:**
- `annotation` (str, optional): Custom annotation string. Uses instance annotation if not provided.

**Returns:**
- `list[str]`: List of extracted type names

### ValidationResult

A Pydantic model representing the validation result.

#### Attributes

- `validated_type` (str): The validated annotation with proper module prefixes
- `errors` (list[Exception]): List of errors encountered during validation
- `pytype` (typing.Any | None): The actual Python type object if validation succeeded
- `invalid_names` (list[str]): List of names that failed validation
- `type_map` (dict[str, str]): Mapping of type names to their import origins

#### Properties

##### `is_valid -> bool`

Returns `True` if validation was successful (no invalid names and pytype is available).

#### Methods

##### `get_origin(type_name: str) -> str | None`

Gets the module origin of a specific type name.

**Parameters:**
- `type_name` (str): The name of the type

**Returns:**
- `str | None`: The origin module or None if not found

## Examples

### Basic Type Validation

```python
validator = TypeValidator('list[str]')
result = validator.validate_names()

print(result.validated_type)  # builtins.list[builtins.str]
print(result.type_map)        # {'list': 'builtins', 'str': 'builtins'}
```

### Complex Generic Types

```python
validator = TypeValidator('Dict[str, Optional[List[int]]]')
result = validator.validate_names()

print(result.validated_type)
# typing.Dict[builtins.str, typing.Optional[builtins.list[builtins.int]]]
```

### Error Handling

```python
validator = TypeValidator('InvalidType[str]')
result = validator.validate_names()

print(result.is_valid)        # False
print(result.invalid_names)   # ['InvalidType']
print(result.errors)          # List of validation errors
```

### Callable Types

```python
validator = TypeValidator('Callable[[str, int], bool]')
result = validator.validate_names()

print(result.validated_type)
# typing.Callable[[builtins.str, builtins.int], builtins.bool]
```

## Supported Namespaces

The validator automatically recognizes and handles types from:

- `builtins`: Built-in Python types (int, str, list, dict, etc.)
- `typing`: Standard typing module types (Union, Optional, Generic, etc.)
- `typing_extensions`: Extended typing features

## Safety Features

- **Safe Import Resolution**: Uses `safelib` to ensure only safe, known types are resolved
- **Input Validation**: Validates annotation strings before processing
- **Error Isolation**: Catches and reports errors without crashing
- **Name Sanitization**: Prevents injection of unsafe code through type names

## Performance

The validator uses compiled regex patterns for efficient name extraction and handles complex nested types with minimal performance overhead.

## Contributing

Contributions are welcome! Please ensure all code follows the existing style and includes appropriate tests.

## License

This project is licensed under the GPL License.

## Dependencies

- `safelib>=0.6.0`: For safe import resolution and validation
- `pydantic`: For result model validation
- `typing_extensions`: For extended typing support

## Compatibility

- Python 3.10+
- Supports all standard typing constructs
- Compatible with both `typing` and `typing_extensions` modules
