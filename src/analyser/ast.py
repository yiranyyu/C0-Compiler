from exception.analyser_exceptions import AstException
from tokenizer import Token


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
        self.children = []
        # print(f'==>[Parsing] {self.type}')

    def add_child(self, ast):
        self.children.append(ast)

    def get_children(self):
        return self.children

    def draw(self):
        print(self.__draw_iter(indent=0))

    def __draw_iter(self, indent: int, islast=False):
        string = ''
        if self.token is None:
            string += f'{" " * indent}{"`-" if islast else "|-"}{get_level_color(indent)}{self.type.lower()}{ConsoleColors.END}\n'
            for idx, child in enumerate(self.children):
                string += ' ' * indent
                lines = child._Ast__draw_iter(
                    indent=indent + 1, islast=(idx == len(self.children) - 1)).split('\n')
                lines = [(line[:indent] + line[indent:])
                         for line in lines if line]
                string += '\n'.join(lines) + '\n'
        else:
            string += f'{" " * indent}|-{get_level_color(indent)}token{ConsoleColors.END} @type={self.token.tok_type}, {ConsoleColors.FAIL}@value={repr(self.token.value)}{ConsoleColors.END}\n'
        return string
