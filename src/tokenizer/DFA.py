class DFA(object):
    INIT = 'INIT'
    IDENTIFIER = 'IDENTIFIER'

    HEX_X = 'HEX_X'
    HEX = 'HEX'
    ZERO = 'ZERO'
    NOT_ZERO_INTEGER = 'NOT_ZERO_INTEGER'

    FLOAT_DOT = 'FLOAT_DOT'
    FLOAT_HEAD = 'FLOAT_HEAD'
    FLOAT_TAIL = 'FLOAT_TAIL'
    FLOAT_EXP_ST = 'FLOAT_EXP_ST'
    FLOAT_EXP_ED = 'FLOAT_EXP_ED'
    FLOAT_EXP_SIGN = 'FLOAT_EXP_SIGN'

    # single-char op
    # ( ) { } , : ; * + -
    SINGLE_CHAR_OP = 'SINGLE_CHAR_OP'

    # double-char op head or single-char op
    DIV = 'DIV'
    EXCL = '!'
    ASSIGN = '='
    LESS = '<'
    GREATER = '>'

    # double-char op
    LEQ = '<='
    GEQ = '>='
    NEQ = '!='
    EQ = '=='

    # comment
    MULTI_LINE_COMMENT_VAL_NOT_STAR = 'MULTI_LINE_COMMENT_VAL_NOT_STAR'
    MULTI_LINE_COMMENT_VAL_STAR = 'MULTI_LINE_COMMENT_VAL_STAR'
    MULTI_LINE_COMMENT_ED = 'MULTI_LINE_COMMENT_ED'
    LINE_COMMENT_VAL = 'LINE_COMMENT_VAL'
    LINE_COMMENT_ED = 'LINE_COMMENT_ED'

    # char
    CHAR_ST = 'CHAR_ST'
    CHAR_ED = 'CHAR_ED'
    CHAR_VAL = 'CHAR_VAL'

    # string
    STR_ST = 'STR_ST'
    STR_ED = 'STR_ED'
    STR_VAL = 'STR_VAL'
