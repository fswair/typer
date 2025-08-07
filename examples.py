from validator import TypeValidator

code = 'Union[Callable[[], int], int]'

validator = TypeValidator(code)

validation = validator.validate_names()

print(validation)

#> validated_type='typing.Union[typing.Callable[[], builtins.int], builtins.int]'
# errors=[] pytype=typing.Union[typing.Callable[[], int], int] invalid_names=[]
# type_map={'int': 'builtins', 'Callable': 'typing', 'Union': 'typing'}

print(validation.pytype)
#> typing.Union[typing.Callable[[], int], int]

print(validation.validated_type)
#> typing.Union[typing.Callable[[], builtins.int], builtins.int]
