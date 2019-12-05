from tokenizer.token import Token


class AnalyserException(Exception):
    def __init__(self, pos: tuple, msg: str):
        super().__init__(f'AnalyserException at (row, col) = {pos[0] + 1, pos[1] + 1}: \033[91m{msg}\033[0m')
        self.row = pos[0]
        self.col = pos[1]


class UnknownVariableType(AnalyserException):
    def __init__(self, pos: tuple, type_str: str):
        super().__init__(pos, f'Unknown type {type_str}')


class InvalidConstantDeclaration(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidVariableDeclaration(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class DuplicateSymbol(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class SymbolNotFound(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class ExpectedIdentifier(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class ExpectedInt32(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class ExpectedReturnType(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class ExpectedTypeSpecifier(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expect type specifier')


class ExpectedSymbol(AnalyserException):
    def __init__(self, pos: tuple, symbol: str):
        super().__init__(pos, f'Expected {symbol}')


class ExpectedCharLiteral(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expected character-literal')


class ExpectedStrLiteral(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expected string-literal')


class ExpectedFloatLiteral(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expected float-literal')


class InvalidFunctionDefinition(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidArgumentDeclaration(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MissingFunctionBody(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidStatement(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid statement')


class InvalidExpression(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid expression')


class InvalidFactor(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidIfStatement(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid if statement')


class InvalidSwitchStatement(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid switch statement')


class InvalidWhileStatement(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidAssignment(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidReturn(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidScanf(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidPrintf(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidCall(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class InvalidCondition(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class LessArguments(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MoreArguments(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class AssignToConstant(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class AssignToFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class AssignWithDeclaration(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MissingMain(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MissingSemicolon(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class MissingSentence(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class ReturnValueForVoidFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class NoReturnValueForIntFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class NotCallingFunction(AnalyserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'')


class TokenIndexOutOfRange(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class AstException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
