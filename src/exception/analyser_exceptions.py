class AnalyserException(Exception):
    def __init__(self, pos: tuple, msg: str):
        super().__init__(
            f'AnalyserException at (row, col) = {pos[0] + 1, pos[1] + 1}: \033[91m{msg}\033[0m')
        self.row = pos[0]
        self.col = pos[1]


class ConstantNotInitialized(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Constant variable not initialized')


class DuplicateSymbol(AnalyserException):
    def __init__(self, pos: tuple, symbol_name):
        super().__init__(pos,
                         f'{symbol_name} already defined at current scope')


class UndefinedSymbol(AnalyserException):
    def __init__(self, pos: tuple, symbol_name: str):
        super().__init__(pos,
                         f'Symbol {symbol_name} is not declared before reference.')


class NoReturnValueForNotVoidFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Function with return_type not void must return value')


class NotCallingFunction(AnalyserException):
    def __init__(self, pos: tuple, symbol_name: str):
        super().__init__(pos, f'{symbol_name} is not a function name')


class FunctionNotDefined(AnalyserException):
    def __init__(self, pos: tuple, func_name: str):
        super().__init__(pos, f'function {func_name} is not defined')


class ReturnValueForVoidFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Cannot return value from void function')


class MissingMain(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'`main` not defined, which is compulsory in C0')


class AssignToConstant(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Cannot assign to const variable')


class ArgumentsNumberNotMatchException(AnalyserException):
    def __init__(self, pos: tuple, expected: int, received: int):
        super().__init__(pos,
                         f'Expected {expected} arguments but got {received}')


class VoidVariableException(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Cannot define void or const void variable')


class UnknownVariableType(AnalyserException):
    def __init__(self, pos: tuple, type_: str):
        super().__init__(pos, f'Unknown type {type_}')


class NotSupportedFeature(AnalyserException):
    def __init__(self, pos: tuple, feature: str):
        super().__init__(pos, f'Feature {feature} not supported yet!')


class VoidTypeCalculationNotSupported(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Cannot calculate with void type')


class FunctionRedefinitionException(AnalyserException):
    def __init__(self, pos: tuple, func_name: str):
        super().__init__(pos, f'function {func_name} already defined')


class FunctionTypeCalculationNotSupported(AnalyserException):
    def __init__(self, pos: tuple, func_name: str):
        super().__init__(pos, f'{func_name} is a function name')
