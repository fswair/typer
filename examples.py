from validator import validate_names

code = 'Union[Callable[[], int], int]'

validated_code = validate_names(code=code)

print(validated_code)
#> typing.Union[typing.Callable[[], builtins.int], builtins.int]

validate_types('FooBar', 'str') # NameError `FooBar`
validate_types('int', 'str') # None, it means validated
