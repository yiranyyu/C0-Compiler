from exception.tokenizer_exceptions import CharOverflow, Integer32Overflow


class TokenType(object):
    IDENTIFIER = 'IDENTIFIER'
    INTEGER_LITERAL = 'INTEGER_LITERAL'
    FLOAT_LITERAL = 'FLOAT_LITERAL'
    STR_LITERAL = 'STR_LITERAL'
    CHAR_LITERAL = 'CHAR_LITERAL'

    # operators
    ADD = 'ADD'
    SUB = 'SUB'
    MUL = 'MUL'
    DIV = 'DIV'
    ASSIGN = 'ASSIGN'
    LEFT_PARENTHESES = 'LEFT_PARENTHESES'
    RIGHT_PARENTHESES = 'RIGHT_PARENTHESES'
    LEFT_BRACE = 'LEFT_BRACE'
    RIGHT_BRACE = 'RIGHT_BRACE'
    COMMA = 'COMMA'
    COLON = 'COLON'
    SEMICOLON = 'SEMICOLON'
    LESS = 'LESS'
    LEQ = 'LEQ'
    GREATER = 'GREATER'
    GEQ = 'GEQ'
    NEQ = 'NEQ'
    EQ = 'EQ'

    # reserved-words
    CONST = 'CONST'
    VOID = 'VOID'
    INT = 'INT'
    CHAR = 'CHAR'
    DOUBLE = 'DOUBLE'
    STRUCT = 'STRUCT'
    IF = 'IF'
    ELSE = 'ELSE'
    SWITCH = 'SWITCH'
    CASE = 'CASE'
    DEFAULT = 'DEFAULT'
    WHILE = 'WHILE'
    FOR = 'FOR'
    DO = 'DO'
    RETURN = 'RETURN'
    BREAK = 'BREAK'
    CONTINUE = 'CONTINUE'
    PRINT = 'PRINT'
    SCAN = 'SCAN'

    types = [VOID, INT, CHAR, DOUBLE]
    relations = [LESS, GREATER, LEQ, GEQ, EQ, NEQ]


class Token(object):
    def __init__(self, literal: str, tok_type: TokenType, st: tuple, ed: tuple):
        """
        st: (row:int, col:int) start position of token, inclusive
        ed: (row:int, col:int) end position of token, exclusive
        tok_type: type of token
        literal: literal representation of token in source code
        """
        self.literal = literal
        self.tok_type = tok_type
        for pos in [st, ed]:
            assert len(pos) == 2, f'pos must be two elements, not {len(pos)}'
            row, col = pos
            assert type(row) is int, f'row must be int, not {type(row)}'
            assert type(col) is int, f'col must be int, not {type(col)}'
        self.st_pos = st
        self.ed_pos = ed
        self.value = self.__init_value()

    def __str__(self):
        return f'@literal={"# " + self.literal + " #" :>15}, @type={self.tok_type :<16}, @val={repr(self.value) :>10}, @pos={(self.st_pos, self.ed_pos)}'

    def __check_char_overflow(self, c: str):
        if ord(c) < 0 or ord(c) > 255:
            raise CharOverflow(self.st_pos[0], self.st_pos[1], c)

    def __check_int_overflow(self, integer: int):
        min_int = -2147483648
        max_int = 2147483647
        if integer < min_int or integer > max_int:
            raise Integer32Overflow(self.st_pos[0], self.st_pos[1], integer)

    def __init_value(self):
        if self.tok_type == TokenType.INTEGER_LITERAL:
            integer = eval(self.literal)
            self.__check_int_overflow(integer)
            return integer
        elif self.tok_type == TokenType.FLOAT_LITERAL:
            return eval(self.literal)
        elif self.tok_type == TokenType.CHAR_LITERAL:
            c = eval(self.literal)
            self.__check_char_overflow(c)
            return c
        elif self.tok_type == TokenType.STR_LITERAL:
            s = eval(self.literal)
            for c in s:
                self.__check_char_overflow(c)
            return s
        return self.literal
