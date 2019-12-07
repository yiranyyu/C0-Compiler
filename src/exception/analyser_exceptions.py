class AnalyserException(Exception):
    def __init__(self, pos: tuple, msg: str):
        super().__init__(
            f'AnalyserException at (row, col) = {pos[0] + 1, pos[1] + 1}: \033[91m{msg}\033[0m')
        self.row = pos[0]
        self.col = pos[1]


class InvalidConstantDeclaration(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class DuplicateSymbol(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class SymbolNotFound(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidArgumentDeclaration(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MissingFunctionBody(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class NoReturnValueForIntFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class NotCallingFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class ReturnValueForVoidFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MissingMain(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class AssignToFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class AssignToConstant(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class LessArguments(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MoreArguments(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')
