from exception.tokenizer_exceptions import *
from tokenizer.DFA import DFA
from tokenizer.charsets import CharSets
from tokenizer.token import Token, TokenType

reserved_words = [
    'const',
    'void', 'int', 'char', 'double',
    'struct',
    'if', 'else',
    'switch', 'case', 'default',
    'while', 'for', 'do',
    'return', 'break', 'continue',
    'print', 'scan'
]


def is_blank(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    return char in CharSets.blank_chars


def is_digit(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    return char in CharSets.digit_chars


def is_punc(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    return char in CharSets.punc_chars


def is_alpha(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    return char in CharSets.alpha_chars


def is_valid_char(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    checks = [is_blank, is_digit, is_punc, is_alpha]
    return any(check(char) for check in checks)


def is_base_char(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    if char in CharSets.not_base_chars:
        return False
    return is_valid_char(char)


def is_s_char(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    if char in ['"', '\\', '\n', '\r']:
        return False
    return is_valid_char(char)


def is_c_char(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    if char in ['\'', '\\', '\n', '\r']:
        return False
    return is_valid_char(char)


def is_hex_digit(char: str):
    assert len(char) == 1, 'char must be `str` that have size = 1'
    is_legal_alpha = char.lower() in ['a', 'b', 'c', 'd', 'e', 'f']
    return is_legal_alpha or is_digit(char)


class Tokenizer(object):
    def __init__(self, source: str):
        self.source = list(map(lambda x: x + '\n', source.split('\n')))
        self.end_row = len(self.source) - 1
        self.end_col = len(self.source[-1]) - 1

        # next position
        self.row = 0
        self.col = 0

    def next_token(self):
        state = DFA.INIT
        token = ''
        st_pos = ...

        def unread_and_return_token(tok_type: TokenType):
            ed_pos = self.__current_pos()
            rtn = Token(literal=token, tok_type=tok_type, st=st_pos, ed=ed_pos)
            self.__unread_char()
            return rtn

        def return_single_char_op():
            op_to_type = {
                '(': TokenType.LEFT_PARENTHESES,
                ')': TokenType.RIGHT_PARENTHESES,
                '{': TokenType.LEFT_BRACE,
                '}': TokenType.RIGHT_BRACE,
                ',': TokenType.COMMA,
                ':': TokenType.COLON,
                ';': TokenType.SEMICOLON,
                '*': TokenType.MUL,
                '+': TokenType.ADD,
                '-': TokenType.SUB,
                '/': TokenType.DIV
            }
            op = token
            if op not in op_to_type:
                raise IllegalSingleCharOp(self.row, self.col, op)
            tok_type = op_to_type[op]
            return unread_and_return_token(tok_type)

        def return_identifier():
            # print(f'identifier @token is "{token}"')
            if token in reserved_words:
                key_to_type = {
                    'const': TokenType.CONST,
                    'void': TokenType.VOID,
                    'int': TokenType.INT,
                    'char': TokenType.CHAR,
                    'double': TokenType.DOUBLE,
                    'struct': TokenType.STRUCT,
                    'if': TokenType.IF,
                    'else': TokenType.ELSE,
                    'switch': TokenType.SWITCH,
                    'case': TokenType.CASE,
                    'default': TokenType.DEFAULT,
                    'while': TokenType.WHILE,
                    'for': TokenType.FOR,
                    'do': TokenType.DO,
                    'return': TokenType.RETURN,
                    'break': TokenType.BREAK,
                    'continue': TokenType.CONTINUE,
                    'print': TokenType.PRINT,
                    'scan': TokenType.SCAN,
                }
                return unread_and_return_token(tok_type=key_to_type[token])
            else:
                return unread_and_return_token(tok_type=TokenType.IDENTIFIER)

        while True:
            next_char = self.__next_char()
            if not next_char:
                return None
            if not is_valid_char(next_char):
                if state not in [DFA.LINE_COMMENT_VAL,
                                 DFA.MULTI_LINE_COMMENT_VAL_NOT_STAR,
                                 DFA.MULTI_LINE_COMMENT_VAL_STAR]:
                    raise InvalidCharacter(self.row, self.col, next_char)

            if state == DFA.INIT:
                if is_blank(next_char):
                    state = DFA.INIT
                elif next_char in '(){},:;*+-':
                    state = DFA.SINGLE_CHAR_OP
                elif next_char == '0':
                    state = DFA.ZERO
                elif is_digit(next_char):
                    state = DFA.NOT_ZERO_INTEGER
                elif next_char == '.':
                    state = DFA.FLOAT_DOT
                elif is_alpha(next_char):
                    state = DFA.IDENTIFIER
                elif next_char == '/':
                    state = DFA.DIV
                elif next_char == '=':
                    state = DFA.ASSIGN
                elif next_char == '!':
                    state = DFA.EXCL
                elif next_char == '<':
                    state = DFA.LESS
                elif next_char == '>':
                    state = DFA.GREATER
                elif next_char == '\'':
                    state = DFA.CHAR_ST
                elif next_char == '"':
                    state = DFA.STR_ST
                else:
                    raise UnexpectedStartOfToken(
                        self.row, self.col, next_char)

                if state == DFA.INIT:
                    continue
                st_pos = self.__current_pos()

            elif state == DFA.IDENTIFIER:
                if is_alpha(next_char) or is_digit(next_char):
                    state = DFA.IDENTIFIER
                else:
                    state = DFA.INIT

                if state == DFA.INIT:
                    return return_identifier()

            # integer
            elif state == DFA.HEX_X:
                if is_hex_digit(next_char):
                    state = DFA.HEX
                else:
                    raise InvalidInputForState(
                        self.row, self.col, next_char, state)
            elif state == DFA.HEX:
                if is_hex_digit(next_char):
                    state = DFA.HEX
                else:
                    state = DFA.INIT

                if state == DFA.INIT:
                    return unread_and_return_token(tok_type=TokenType.INTEGER_LITERAL)
            elif state == DFA.ZERO:
                if next_char in 'xX':
                    state = DFA.HEX_X
                elif is_digit(next_char):
                    state = DFA.FLOAT_HEAD
                elif next_char == '.':
                    state = DFA.FLOAT_DOT
                elif next_char in 'eE':
                    state = DFA.FLOAT_EXP_ST
                else:
                    state = DFA.INIT

                if state == DFA.INIT:
                    return unread_and_return_token(tok_type=TokenType.INTEGER_LITERAL)
            elif state == DFA.NOT_ZERO_INTEGER:
                if next_char == '.':
                    state = DFA.FLOAT_DOT
                elif next_char in 'Ee':
                    state = DFA.FLOAT_EXP_ST
                elif is_digit(next_char):
                    state = DFA.NOT_ZERO_INTEGER
                else:
                    state = DFA.INIT

                if state == DFA.INIT:
                    return unread_and_return_token(tok_type=TokenType.INTEGER_LITERAL)

            # float
            elif state == DFA.FLOAT_DOT:
                if is_digit(next_char):
                    state = DFA.FLOAT_TAIL
                elif next_char in 'eE':
                    state = DFA.FLOAT_EXP_ST
                else:
                    state = DFA.INIT

                if state == DFA.INIT:
                    return unread_and_return_token(tok_type=TokenType.FLOAT_LITERAL)
            elif state == DFA.FLOAT_HEAD:
                if is_digit(next_char):
                    state = DFA.FLOAT_HEAD
                elif next_char == '.':
                    state = DFA.FLOAT_DOT
                elif next_char in 'eE':
                    state = DFA.FLOAT_EXP_ST
                else:
                    raise InvalidInputForState(
                        self.row, self.col, next_char, state)
            elif state == DFA.FLOAT_TAIL:
                if is_digit(next_char):
                    state = DFA.FLOAT_TAIL
                elif next_char in 'eE':
                    state = DFA.FLOAT_EXP_ST
                else:
                    state = DFA.INIT

                if state == DFA.INIT:
                    return unread_and_return_token(tok_type=TokenType.FLOAT_LITERAL)
            elif state == DFA.FLOAT_EXP_ST:
                if next_char in '+-':
                    state = DFA.FLOAT_EXP_SIGN
                elif is_digit(next_char):
                    state = DFA.FLOAT_EXP_ED
                else:
                    raise InvalidInputForState(
                        self.row, self.col, next_char, state)
            elif state == DFA.FLOAT_EXP_SIGN:
                if is_digit(next_char):
                    state = DFA.FLOAT_EXP_ED
                else:
                    raise InvalidInputForState(
                        self.row, self.col, next_char, state)
            elif state == DFA.FLOAT_EXP_ED:
                if is_digit(next_char):
                    state = DFA.FLOAT_EXP_ED
                else:
                    state = DFA.INIT

                if state == DFA.INIT:
                    return unread_and_return_token(tok_type=TokenType.FLOAT_LITERAL)

            # single-char op
            elif state == DFA.SINGLE_CHAR_OP:
                return return_single_char_op()
            elif state == DFA.DIV:
                if next_char == '*':
                    state = DFA.MULTI_LINE_COMMENT_VAL_NOT_STAR
                elif next_char == '/':
                    state = DFA.LINE_COMMENT_VAL
                else:
                    return return_single_char_op()
            elif state == DFA.EXCL:
                if next_char == '=':
                    state = DFA.NEQ
                else:
                    raise InvalidInputForState(
                        self.row, self.col, next_char, state)
            elif state == DFA.ASSIGN:
                if next_char == '=':
                    state = DFA.EQ
                else:
                    return unread_and_return_token(tok_type=TokenType.ASSIGN)
            elif state == DFA.LESS:
                if next_char == '=':
                    state = DFA.LEQ
                else:
                    return unread_and_return_token(tok_type=TokenType.LESS)
            elif state == DFA.GREATER:
                if next_char == '=':
                    state = DFA.GEQ
                else:
                    return unread_and_return_token(tok_type=TokenType.GREATER)

            # double-char op
            elif state == DFA.LEQ:
                return unread_and_return_token(tok_type=TokenType.LEQ)
            elif state == DFA.GEQ:
                return unread_and_return_token(tok_type=TokenType.GEQ)
            elif state == DFA.NEQ:
                return unread_and_return_token(tok_type=TokenType.NEQ)
            elif state == DFA.EQ:
                return unread_and_return_token(tok_type=TokenType.EQ)

            # comment
            elif state == DFA.MULTI_LINE_COMMENT_VAL_NOT_STAR:
                if next_char == '*':
                    state = DFA.MULTI_LINE_COMMENT_VAL_STAR
                else:
                    state = DFA.MULTI_LINE_COMMENT_VAL_NOT_STAR
            elif state == DFA.MULTI_LINE_COMMENT_VAL_STAR:
                if next_char == '/':
                    state = DFA.MULTI_LINE_COMMENT_ED
                elif next_char == '*':
                    state = DFA.MULTI_LINE_COMMENT_VAL_STAR
                else:
                    state = DFA.MULTI_LINE_COMMENT_VAL_NOT_STAR
            elif state == DFA.MULTI_LINE_COMMENT_ED:
                # print(f'Read multiline comment "{token}"')
                self.__unread_char()
                state = DFA.INIT
                token = ''
                continue
            elif state == DFA.LINE_COMMENT_VAL:
                if ord(next_char) in [0x0A, 0x0D]:
                    state = DFA.LINE_COMMENT_ED
                else:
                    state = DFA.LINE_COMMENT_VAL
            elif state == DFA.LINE_COMMENT_ED:
                # print(f'Read line comment "{token}"')
                self.__unread_char()
                state = DFA.INIT
                token = ''
                continue

            # char
            elif state == DFA.CHAR_ST:
                # print(f'@char read {next_char}')
                if is_c_char(next_char):
                    state = DFA.CHAR_VAL
                else:
                    self.__unread_char()
                    esc = self.__read_escape_seq()
                    state = DFA.CHAR_VAL
                    token += esc
                    continue

            elif state == DFA.CHAR_VAL:
                if next_char == '\'':
                    state = DFA.CHAR_ED
                else:
                    raise InvalidInputForState(
                        self.row, self.col, next_char, state)
            elif state == DFA.CHAR_ED:
                return unread_and_return_token(TokenType.CHAR_LITERAL)

            # string
            elif state == DFA.STR_ST:
                if is_s_char(next_char):
                    state = DFA.STR_VAL
                else:
                    self.__unread_char()
                    esc = self.__read_escape_seq()
                    state = DFA.STR_VAL
                    token += esc
                    continue
            elif state == DFA.STR_VAL:
                if next_char == '"':
                    state = DFA.STR_ED
                elif is_s_char(next_char):
                    state = DFA.STR_VAL
                else:
                    self.__unread_char()
                    esc = self.__read_escape_seq()
                    state = DFA.STR_VAL
                    token += esc
                    continue
            elif state == DFA.STR_ED:
                return unread_and_return_token(TokenType.STR_LITERAL)

            token += next_char

    def all_tokens(self):
        tokens = []
        while True:
            token = self.next_token()
            if token is None:
                return tokens
            tokens.append(token)

    def __current_pos(self):
        return self.row, self.col

    def __previous_pos(self):
        self.__unread_char()
        row, col = self.__current_pos()
        self.__next_char()
        return row, col

    def __next_char(self):
        if self.is_eof():
            return ''
        c = self.source[self.row][self.col]
        # print(f'[read-char] "{c}"')
        self.__move_to_next_pos()
        return c

    def __unread_char(self):
        if self.col == 0 and self.row == 0:
            raise IndexError(
                'cannot unread char from the beginning of source code')

        self.col -= 1
        if self.col == -1:
            self.row -= 1
            self.col = len(self.source[self.row]) - 1
        # print(f'[unread] "{self.source[self.row][self.col]}')

    def __move_to_next_pos(self):
        self.col += 1
        if self.col == len(self.source[self.row]):
            self.row += 1
            self.col = 0

    def is_eof(self):
        # for the case that input file is empty and `self.end_row` is -1
        if self.row > self.end_row:
            return True
        return self.row == self.end_row and self.col > self.end_col

    def __read_escape_seq(self):
        """
        Read a whole escape sequence, which is
        <escape-seq> ::=
            '\\' | "\'" | '"' | '\n' | '\r' | '\t'
            | '\\x'<hexadecimal-digit><hexadecimal-digit>
        """
        if self.__next_char() != '\\':
            raise IllegalEscapeSequenceException(self.row, self.col,
                                                 msg='try to read a escape-seq when first character is not \\')

        next_char = self.__next_char()
        if next_char in ['\\', '\'', '"', 'n', 'r', 't']:
            return '\\' + next_char
        elif next_char == 'x':
            chars = 'x'
            for i in range(2):
                next_char = self.__next_char()
                if not next_char:
                    raise IllegalEscapeSequenceException(self.row, self.col,
                                                         msg='Incomplete hex esc-seq')
                elif not is_hex_digit(next_char):
                    raise IllegalEscapeSequenceException(self.row, self.col,
                                                         msg=f'Except hexdecimal digit, while get {next_char}')
                chars += next_char
            return '\\' + chars
        else:
            raise IllegalEscapeSequenceException(self.row, self.col,
                                                 msg=f'Illegal esc-seq start with \\{next_char}')
