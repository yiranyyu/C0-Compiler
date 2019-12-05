class TokenizerException(BaseException):
    def __init__(self, row: int, col: int, msg: str):
        super().__init__(f'Error at {(row, col)}, {msg}')
        self.row = row
        self.col = col


class IllegalEscapeSequenceException(TokenizerException):
    def __init__(self, row, col, msg):
        super().__init__(row, col, msg)


class UnexpectedStartOfToken(TokenizerException):
    def __init__(self, row, col, c: str):
        super().__init__(row, col, f'{c} is not a valid start character')


class InvalidCharacter(TokenizerException):
    def __init__(self, row, col, c: str):
        super().__init__(row, col, f'{c} is not a valid character')


class InvalidInputForState(TokenizerException):
    def __init__(self, row, col, input_char: str, state: str):
        super().__init__(
            row, col, f'{input_char} is not valid input for state {state}')


class IllegalSingleCharOp(TokenizerException):
    def __init__(self, row, col, op):
        super().__init__(row, col, f'{op} is not a valid single-char op')


class CharOverflow(TokenizerException):
    def __init__(self, row, col, c):
        super().__init__(row, col,
                         f'character #{c}# cannot be represent in 1 byte, since ord(c) is {ord(c)}')


class Integer32Overflow(TokenizerException):
    def __init__(self, row, col, integer: int):
        super().__init__(row, col, f'integer {integer} out of range')
