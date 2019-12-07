from tokenizer.token import Token


class ParserException(Exception):
    def __init__(self, pos: tuple, msg: str):
        super().__init__(
            f'ParserException at (row, col) = {pos[0] + 1, pos[1] + 1}: \033[91m{msg}\033[0m')
        self.row = pos[0]
        self.col = pos[1]


class UnknownVariableType(ParserException):
    def __init__(self, pos: tuple, type_str: str):
        super().__init__(pos, f'Unknown type {type_str}')


class ExpectedTypeSpecifier(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expect type specifier')


class ExpectedSymbol(ParserException):
    def __init__(self, pos: tuple, symbol: str):
        super().__init__(pos, f'Expected {symbol}')


class ExpectedCharLiteral(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expected character-literal')


class ExpectedStrLiteral(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expected string-literal')


class ExpectedFloatLiteral(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expected float-literal')


class ExpectedInt32(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expect int32 literal')


class ExpectedIdentifier(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Expected identifier')


class InvalidVariableDeclaration(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid variable declaration')


class InvalidFunctionDefinition(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid function definition')


class InvalidStatement(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid statement')


class InvalidExpression(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid expression')


class InvalidIfStatement(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid if statement')


class InvalidSwitchStatement(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Invalid switch statement')


class MissingSemicolon(ParserException):
    def __init__(self, pos: tuple):
        super().__init__(pos, f'Missing semicolon')


class TokenIndexOutOfRange(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class AstException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
