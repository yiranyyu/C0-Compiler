from exception.parser_exceptions import AstException
from tokenizer import Token
from typing import List


class ConsoleColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_level_color(level):
    colors = [
        '\033[95m',
        '\033[94m',
        '\033[93m',
        '\033[92m',
        '\033[1m',
    ]
    return colors[level % len(colors)]


class AstType(object):
    C0 = '<C0-root>'
    VARIABLE_DECLARATION = 'VARIABLE_DECLARATION'
    FUNCTION_DEFINITION = 'FUNCTION_DEFINITION'

    TYPE_SPECIFIER = 'TYPE_SPECIFIER'
    INIT_DECLARATOR_LIST = 'INIT_DECLARATOR_LIST'
    INIT_DECLARATOR = 'INIT_DECLARATOR'
    INITIALIZER = 'INITIALIZER'
    ASSIGNMENT_EXPRESSION = 'ASSIGNMENT_EXPRESSION'
    EXPRESSION = 'EXPRESSION'
    ADDITIVE_EXPRESSION = 'ADDITIVE_EXPRESSION'
    MULTIPLICATIVE_EXPRESSION = 'MULTIPLICATIVE_EXPRESSION'
    CAST_EXPRESSION = 'CAST_EXPRESSION'
    UNARY_EXPRESSION = 'UNARY_EXPRESSION'
    PRIMARY_EXPRESSION = 'PRIMARY_EXPRESSION'
    FUNCTION_CALL = 'FUNCTION_CALL'
    EXPRESSION_LIST = 'EXPRESSION_LIST'
    PARAMETER_CLAUSE = 'PARAMETER_CLAUSE'
    PARAMETER_DECLARATION_LIST = 'PARAMETER_DECLARATION_LIST'
    PARAMETER_DECLARATION = 'PARAMETER_DECLARATION'
    COMPOUND_STATEMENT = 'COMPOUND_STATEMENT'
    STATEMENT_SEQ = 'STATEMENT_SEQ'
    STATEMENT = 'STATEMENT'
    CONDITION_STATEMENT = 'CONDITION_STATEMENT'
    LABELED_STATEMENT = 'LABELED_STATEMENT'
    LOOP_STATEMENT = 'LOOP_STATEMENT'
    FOR_INIT_STATEMENT = 'FOR_INIT_STATEMENT'
    FOR_UPDATE_STATEMENT = 'FOR_UPDATE_STATEMENT'
    JUMP_STATEMENT = 'JUMP_STATEMENT'
    RETURN_STATEMENT = 'RETURN_STATEMENT'
    SCAN_STATEMENT = 'SCAN_STATEMENT'
    PRINT_STATEMENT = 'PRINT_STATEMENT'
    PRINTABLE_LIST = 'PRINTABLE_LIST'
    PRINTABLE = 'PRINTABLE'
    CONDITION = 'CONDITION'

    IDENTIFIER = 'IDENTIFIER'
    INTEGER_LITERAL = 'INTEGER_LITERAL'
    CHAR_LITERAL = 'CHAR_LITERAL'
    FLOAT_LITERAL = 'FLOAT_LITERAL'
    STR_LITERAL = 'STR_LITERAL'

    UNARY_OPERATOR = 'UNARY_OPERATOR'
    ADDITIVE_OPERATOR = 'ADDITIVE_OPERATOR'
    MULTIPLICATIVE_OPERATOR = 'MULTIPLICATIVE_OPERATOR'
    RELATIONAL_OPERATOR = 'RELATIONAL_OPERATOR'
    ASSIGNMENT_OPERATOR = 'ASSIGNMENT_OPERATOR'
    CONST_QUALIFIER = 'CONST_QUALIFIER'
    SIMPLE_TYPE_SPECIFIER = 'SIMPLE_TYPE_SPECIFIER'

    TOKEN = 'TOKEN'


class Ast(object):
    def __init__(self, ast_type: str, token: Token = None):
        if ast_type != AstType.TOKEN:
            if token is not None:
                raise AstException(f'Cannot init {ast_type} Ast with token')
        self.type = ast_type
        self.token: Token = token
        self.children: List[Ast] = []
        # print(f'==>[Parsing] {self.type}')

    def add_child(self, ast):
        self.children.append(ast)

    def get_children(self):
        return self.children

    def draw(self, draw_full_ast=False):
        print(self.__draw_iter(indent=0, draw_full_ast=draw_full_ast))

    def __draw_iter(self, indent: int, islast=False, draw_full_ast=False):
        string = ''
        if self.type == AstType.STATEMENT and len(self.children) == 1 and not draw_full_ast:
            string += self.children[0]._Ast__draw_iter(indent=indent,
                                                       islast=islast,
                                                       draw_full_ast=draw_full_ast)
        elif self.token is None:
            string += f'{" " * indent}{"`-" if islast else "|-"}{get_level_color(indent)}{self.type.lower()}{ConsoleColors.END}\n'
            if len(self.children) == 1 and not draw_full_ast:
                children = self.children
                while True:
                    if len(children[0].children) != 1:
                        break
                    children = children[0].children
                string += ' ' * indent
                string += children[0]._Ast__draw_iter(indent=indent+1,
                                                      islast=True,
                                                      draw_full_ast=draw_full_ast)
            else:
                for idx, child in enumerate(self.children):
                    islast = idx == len(self.children) - 1
                    string += ' ' * indent
                    string += child._Ast__draw_iter(indent=indent + 1,
                                                    islast=islast,
                                                    draw_full_ast=draw_full_ast)
        else:
            string += f'{" " * indent}|-{get_level_color(indent)}token{ConsoleColors.END} @type={self.token.tok_type}, {ConsoleColors.FAIL}@value={repr(self.token.value)}{ConsoleColors.END}\n'
        return string
