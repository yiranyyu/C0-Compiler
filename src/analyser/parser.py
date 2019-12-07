import sys
import typing
from tokenizer import Token, TokenType
from exception.parser_exceptions import *
from analyser.ast import Ast, AstType

is_debug = False


def debug(*arg, **kwargs):
    if is_debug:
        print(*arg, **kwargs)


class C0ASTParser(object):
    def __init__(self, tokens: typing.List[Token]):
        self.tokens = tokens
        self.tok_idx = 0
        self.parsed = False
        self.__ast: Ast = ...

    def parse(self) -> Ast:
        if not self.parsed:
            self.__ast = self.__parse_c0()
            self.parsed = True
        return self.__ast

    def __parse_c0(self) -> Ast:
        """
        Analyse C0 program, generate the AST
        <C0-program> ::= {<variable-declaration>}{<function-definition>}
        """

        ast = Ast(AstType.C0)

        # {<variable-declaration>}
        while self.__peek_token(suppress_exception=True) is not None:
            token = self.__peek_token()

            if token.tok_type == TokenType.CONST:
                ast.add_child(self.__parse_variable_declaration())
            elif token.tok_type in TokenType.types:
                a, b, c = [self.__next_token(
                    suppress_exception=True) for i in range(3)]
                if c is None:
                    raise InvalidVariableDeclaration(token.st_pos)

                for _ in range(3):
                    self.__unread_token()

                if c.tok_type == TokenType.LEFT_PARENTHESES:
                    ast.add_child(self.__parse_function_definition())
                    break
                else:
                    ast.add_child(self.__parse_variable_declaration())
            else:
                raise ExpectedTypeSpecifier(token.st_pos)

        # {<function-definition>}
        while self.__peek_token(suppress_exception=True) is not None:
            ast.add_child(self.__parse_function_definition())

        return ast

    def __parse_function_definition(self) -> Ast:
        """
        <function-definition> ::=
            <type-specifier><identifier><parameter-clause><compound-statement>
        """
        ast = Ast(AstType.FUNCTION_DEFINITION)
        start_pos = self.__current_pos()

        try:
            ast.add_child(self.__parse_type_specifier())
            ast.add_child(self.__parse_identifier())
            ast.add_child(self.__parse_parameter_clause())
            ast.add_child(self.__parse_compound_statement())
        except TokenIndexOutOfRange as e:
            print(e, file=sys.stderr)
            raise InvalidFunctionDefinition(start_pos)

        return ast

    def __parse_variable_declaration(self) -> Ast:
        """
        <variable-declaration> ::=
            [<const-qualifier>]<type-specifier><init-declarator-list>';'
        """
        ast = Ast(AstType.VARIABLE_DECLARATION)
        start_pos = self.__current_pos()

        try:
            token = self.__peek_token()
            if token.tok_type == TokenType.CONST:
                ast.add_child(self.__parse_const_qualifier())

            ast.add_child(self.__parse_type_specifier())
            ast.add_child(self.__parse_init_declarator_list())
            ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        except TokenIndexOutOfRange as e:
            print(e, file=sys.stderr)
            raise InvalidVariableDeclaration(start_pos)

        return ast

    def __parse_const_qualifier(self) -> Ast:
        """
        <const-qualifier>        ::= 'const'
        """
        ast = Ast(AstType.CONST_QUALIFIER)
        ast.add_child(self.__assert_token('const', TokenType.CONST))
        return ast

    def __parse_type_specifier(self) -> Ast:
        """
        <type-specifier>         ::= <simple-type-specifier>
        """
        ast = Ast(AstType.TYPE_SPECIFIER)
        ast.add_child(self.__parse_simple_type_specifier())
        return ast

    def __parse_simple_type_specifier(self) -> Ast:
        """
        <simple-type-specifier>  ::= 'void'|'int'|'char'|'double'
        """
        ast = Ast(AstType.SIMPLE_TYPE_SPECIFIER)

        token = self.__next_token()
        if token.tok_type in TokenType.types:
            ast.add_child(Ast(AstType.TOKEN, token))
        else:
            raise UnknownVariableType(token.st_pos, token.literal)

        return ast

    def __parse_init_declarator_list(self) -> Ast:
        """
        <init-declarator-list> ::=
            <init-declarator>{','<init-declarator>}
        """
        ast = Ast(AstType.INIT_DECLARATOR_LIST)

        ast.add_child(self.__parse_init_declarator())

        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None or token.tok_type != TokenType.COMMA:
                break
            ast.add_child(self.__assert_token(',', TokenType.COMMA))
            ast.add_child(self.__parse_init_declarator())
        return ast

    def __parse_init_declarator(self) -> Ast:
        """
        <init-declarator> ::=
            <identifier>[<initializer>]
        """
        ast = Ast(AstType.INIT_DECLARATOR)

        ast.add_child(self.__parse_identifier())

        token = self.__peek_token()
        if token.tok_type == TokenType.ASSIGN:
            ast.add_child(self.__parse_initializer())
        return ast

    def __parse_identifier(self) -> Ast:
        ast = Ast(AstType.IDENTIFIER)

        token = self.__next_token(suppress_exception=True)
        if token is None:
            raise ExpectedIdentifier(self.__prev_token().st_pos)

        if token.tok_type != TokenType.IDENTIFIER:
            raise ExpectedIdentifier(token.st_pos)
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_initializer(self) -> Ast:
        """
        <initializer> ::=
            '='<expression>
        """
        ast = Ast(AstType.INITIALIZER)

        ast.add_child(self.__assert_token('=', TokenType.ASSIGN))
        ast.add_child(self.__parse_expression())
        return ast

    def __parse_expression(self) -> Ast:
        """
        <expression> ::=
            <additive-expression>
        """
        ast = Ast(AstType.EXPRESSION)
        ast.add_child(self.__parse_additive_expression())
        return ast

    def __parse_additive_expression(self) -> Ast:
        """
        <additive-expression> ::=
            <multiplicative-expression>{<additive-operator><multiplicative-expression>}
        """
        ast = Ast(AstType.ADDITIVE_EXPRESSION)

        ast.add_child(self.__parse_multiplicative_expression())

        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None or token.tok_type not in [TokenType.ADD, TokenType.SUB]:
                break
            ast.add_child(self.__parse_additive_operator())
            ast.add_child(self.__parse_multiplicative_expression())
        return ast

    def __parse_multiplicative_expression(self) -> Ast:
        """
        <multiplicative-expression> ::=
            <cast-expression>{<multiplicative-operator><cast-expression>}
        """
        ast = Ast(AstType.MULTIPLICATIVE_EXPRESSION)

        ast.add_child(self.__parse_cast_expression())

        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None or token.tok_type not in [TokenType.MUL, TokenType.DIV]:
                break
            ast.add_child(self.__parse_multiplicative_operator())
            ast.add_child(self.__parse_cast_expression())
        return ast

    def __parse_cast_expression(self) -> Ast:
        """
        <cast-expression> ::=
            {'('<type-specifier>')'}<unary-expression>
        """
        ast = Ast(AstType.CAST_EXPRESSION)

        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None:
                raise InvalidExpression(self.__prev_token().ed_pos)

            if token.tok_type != TokenType.LEFT_PARENTHESES:
                break
            ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))
            ast.add_child(self.__parse_type_specifier())
            ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))

        ast.add_child(self.__parse_unary_expression())
        return ast

    def __parse_unary_expression(self) -> Ast:
        """
        <unary-expression> ::=
            [<unary-operator>]<primary-expression>
        """
        ast = Ast(AstType.UNARY_EXPRESSION)

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise InvalidExpression(self.__prev_token().ed_pos)

        if token.tok_type in [TokenType.ADD, TokenType.SUB]:
            ast.add_child(self.__parse_unary_operator())
        ast.add_child(self.__parse_primary_expression())
        return ast

    def __parse_primary_expression(self) -> Ast:
        """
        <primary-expression> ::=
            '('<expression>')'
            |<identifier>
            |<integer-literal>
            |<char-literal>
            |<floating-literal>
            |<function-call>
        """
        # debug(f'@[parsing] primary expression')
        ast = Ast(AstType.PRIMARY_EXPRESSION)

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise InvalidExpression(self.__prev_token().ed_pos)

        if token.tok_type == TokenType.LEFT_PARENTHESES:
            ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))
            ast.add_child(self.__parse_expression())
            ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
        elif token.tok_type == TokenType.INTEGER_LITERAL:
            ast.add_child(self.__parse_integer_literal())
        elif token.tok_type == TokenType.CHAR_LITERAL:
            ast.add_child(self.__parse_char_literal())
        elif token.tok_type == TokenType.FLOAT_LITERAL:
            ast.add_child(self.__parse_float_literal())
        elif token.tok_type == TokenType.IDENTIFIER:
            self.__next_token()
            token = self.__peek_token(suppress_exception=True)
            if token is None:
                raise MissingSemicolon(self.__prev_token().ed_pos)

            self.__unread_token()
            if token.tok_type == TokenType.LEFT_PARENTHESES:
                ast.add_child(self.__parse_function_call())
            else:
                ast.add_child(self.__parse_identifier())
        return ast

    def __parse_unary_operator(self) -> Ast:
        """
        <unary-operator>          ::= '+' | '-'
        """
        ast = Ast(AstType.UNARY_OPERATOR)

        token = self.__next_token()
        if token.tok_type not in [TokenType.ADD, TokenType.SUB]:
            raise ExpectedSymbol(token.st_pos, '+ or -')
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_additive_operator(self) -> Ast:
        """
        <additive-operator>       ::= '+' | '-'
        """
        ast = Ast(AstType.ADDITIVE_OPERATOR)

        token = self.__next_token()
        if token.tok_type not in [TokenType.ADD, TokenType.SUB]:
            raise ExpectedSymbol(token.st_pos, '+ or -')
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_multiplicative_operator(self) -> Ast:
        """
        <multiplicative-operator> ::= '*' | '/'
        """
        ast = Ast(AstType.MULTIPLICATIVE_OPERATOR)

        token = self.__next_token()
        if token.tok_type not in [TokenType.MUL, TokenType.DIV]:
            raise ExpectedSymbol(token.st_pos, '* or /')
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_relational_operator(self) -> Ast:
        """
        <relational-operator>     ::= '<' | '<=' | '>' | '>=' | '!=' | '=='
        """
        ast = Ast(AstType.RELATIONAL_OPERATOR)

        token = self.__next_token()
        if token.tok_type not in TokenType.relations:
            raise ExpectedSymbol(
                token.st_pos, "'<' | '<=' | '>' | '>=' | '!=' | '=='")
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_assignment_operator(self) -> Ast:
        """
        <assignment-operator>     ::= '='
        """
        ast = Ast(AstType.ASSIGNMENT_OPERATOR)
        ast.add_child(self.__assert_token('=', TokenType.ASSIGN))
        return ast

    def __parse_integer_literal(self) -> Ast:
        ast = Ast(AstType.INTEGER_LITERAL)

        token = self.__next_token()
        if token.tok_type != TokenType.INTEGER_LITERAL:
            raise ExpectedInt32(token.st_pos)
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_char_literal(self) -> Ast:
        ast = Ast(AstType.CHAR_LITERAL)

        token = self.__next_token()
        if token.tok_type != TokenType.CHAR_LITERAL:
            raise ExpectedCharLiteral(token.st_pos)
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_float_literal(self) -> Ast:
        ast = Ast(AstType.FLOAT_LITERAL)

        token = self.__next_token()
        if token.tok_type != TokenType.FLOAT_LITERAL:
            raise ExpectedFloatLiteral(token.st_pos)
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_str_literal(self) -> Ast:
        ast = Ast(AstType.STR_LITERAL)

        token = self.__next_token()
        if token.tok_type != TokenType.STR_LITERAL:
            raise ExpectedStrLiteral(token.st_pos)
        ast.add_child(Ast(AstType.TOKEN, token))
        return ast

    def __parse_function_call(self) -> Ast:
        """
        <function-call> ::=
            <identifier> '(' [<expression-list>] ')'
        """
        ast = Ast(AstType.FUNCTION_CALL)

        ast.add_child(self.__parse_identifier())
        ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise ExpectedSymbol(self.__prev_token().ed_pos, ')')
        if token.tok_type != TokenType.RIGHT_PARENTHESES:
            ast.add_child(self.__parse_expression_list())

        ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
        return ast

    def __parse_expression_list(self) -> Ast:
        """
        <expression-list> ::=
            <expression>{','<expression>}
        """
        ast = Ast(AstType.EXPRESSION_LIST)

        ast.add_child(self.__parse_expression())
        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None or token.tok_type != TokenType.COMMA:
                break
            ast.add_child(self.__assert_token(',', TokenType.COMMA))
            ast.add_child(self.__parse_expression())
        return ast

    def __parse_parameter_clause(self) -> Ast:
        """
        <parameter-clause> ::=
            '(' [<parameter-declaration-list>] ')'
        """
        ast = Ast(AstType.PARAMETER_CLAUSE)

        ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise ExpectedSymbol(self.__prev_token().ed_pos, ')')
        if token.tok_type != TokenType.RIGHT_PARENTHESES:
            ast.add_child(self.__parse_parameter_declaration_list())

        ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
        return ast

    def __parse_parameter_declaration_list(self) -> Ast:
        """
        <parameter-declaration-list> ::=
            <parameter-declaration>{','<parameter-declaration>}
        """
        ast = Ast(AstType.PARAMETER_DECLARATION_LIST)

        ast.add_child(self.__parse_parameter_declaration())
        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None or token.tok_type != TokenType.COMMA:
                break
            ast.add_child(self.__assert_token(',', TokenType.COMMA))
            ast.add_child(self.__parse_parameter_declaration())
        return ast

    def __parse_parameter_declaration(self) -> Ast:
        """
        <parameter-declaration> ::=
            [<const-qualifier>]<type-specifier><identifier>
        """
        ast = Ast(AstType.PARAMETER_DECLARATION)

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise ExpectedTypeSpecifier(self.__prev_token().ed_pos)
        if token.tok_type == TokenType.CONST:
            ast.add_child(self.__parse_const_qualifier())

        ast.add_child(self.__parse_type_specifier())
        ast.add_child(self.__parse_identifier())
        return ast

    def __parse_compound_statement(self) -> Ast:
        """
        <compound-statement> ::=
            '{' {<variable-declaration>} <statement-seq> '}'
        """
        ast = Ast(AstType.COMPOUND_STATEMENT)

        ast.add_child(self.__assert_token('{', TokenType.LEFT_BRACE))
        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None:
                raise ExpectedSymbol(self.__prev_token().ed_pos, '}')
            if token.tok_type not in TokenType.types + [TokenType.CONST]:
                break
            ast.add_child(self.__parse_variable_declaration())

        ast.add_child(self.__parse_statement_seq())
        ast.add_child(self.__assert_token('}', TokenType.RIGHT_BRACE))
        return ast

    def __parse_statement_seq(self) -> Ast:
        """
        <statement-seq> ::=
            {<statement>}
        """
        ast = Ast(AstType.STATEMENT_SEQ)

        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None:
                raise ExpectedSymbol(self.__prev_token().ed_pos, '}')
            elif token.tok_type in [TokenType.LEFT_BRACE,
                                    TokenType.IF, TokenType.SWITCH,
                                    TokenType.WHILE, TokenType.DO, TokenType.FOR,
                                    TokenType.BREAK, TokenType.CONTINUE, TokenType.RETURN,
                                    TokenType.PRINT,
                                    TokenType.SCAN,
                                    TokenType.IDENTIFIER,
                                    TokenType.SEMICOLON]:
                ast.add_child(self.__parse_statement())
            else:
                break
        return ast

    def __parse_statement(self) -> Ast:
        """
        <statement> ::=
            <compound-statement>
            |<condition-statement>
            |<loop-statement>
            |<jump-statement>
            |<print-statement>
            |<scan-statement>
            |<assignment-expression>';'
            |<function-call>';'
            |';'
        """
        ast = Ast(AstType.STATEMENT)

        token = self.__peek_token()
        if token.tok_type == TokenType.LEFT_BRACE:
            ast.add_child(self.__parse_compound_statement())
        elif token.tok_type in [TokenType.IF, TokenType.SWITCH]:
            ast.add_child(self.__parse_condition_statement())
        elif token.tok_type in [TokenType.WHILE, TokenType.DO, TokenType.FOR]:
            ast.add_child(self.__parse_loop_statement())
        elif token.tok_type in [TokenType.BREAK, TokenType.CONTINUE, TokenType.RETURN]:
            ast.add_child(self.__parse_jump_statement())
        elif token.tok_type == TokenType.PRINT:
            ast.add_child(self.__parse_print_statement())
        elif token.tok_type == TokenType.SCAN:
            ast.add_child(self.__parse_scan_statement())
        elif token.tok_type == TokenType.SEMICOLON:
            ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        elif token.tok_type == TokenType.IDENTIFIER:
            self.__next_token()
            token = self.__next_token(suppress_exception=True)
            if token is None:
                raise ExpectedSymbol(self.__prev_token().ed_pos, '( or =')
            if token.tok_type not in [TokenType.ASSIGN, TokenType.LEFT_PARENTHESES]:
                raise ExpectedSymbol(token.st_pos, '( or =')

            self.__unread_token()
            self.__unread_token()
            if token.tok_type == TokenType.ASSIGN:
                ast.add_child(self.__parse_assignment_expression())
                ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
            elif token.tok_type == TokenType.LEFT_PARENTHESES:
                ast.add_child(self.__parse_function_call())
                ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        else:
            raise InvalidStatement(token.st_pos)
        return ast

    def __parse_condition_statement(self) -> Ast:
        """
        <condition-statement> ::=
            'if' '(' <condition> ')' <statement> ['else' <statement>]
            |'switch' '(' <expression> ')' '{' {<labeled-statement>} '}'
        """
        ast = Ast(AstType.CONDITION_STATEMENT)

        token = self.__peek_token()
        if token.tok_type == TokenType.IF:
            try:
                # 'if' '(' <condition> ')' <statement>
                ast.add_child(self.__assert_token('if', TokenType.IF))
                ast.add_child(self.__assert_token(
                    '(', TokenType.LEFT_PARENTHESES))
                ast.add_child(self.__parse_condition())
                ast.add_child(self.__assert_token(
                    ')', TokenType.RIGHT_PARENTHESES))
                ast.add_child(self.__parse_statement())

                # ['else' <statement>]
                token = self.__peek_token(suppress_exception=True)
                if token is not None and (token.tok_type == TokenType.ELSE):
                    ast.add_child(self.__assert_token('else', TokenType.ELSE))
                    ast.add_child(self.__parse_statement())
            except TokenIndexOutOfRange as e:
                print(e, file=sys.stderr)
                raise InvalidIfStatement(self.__prev_token().ed_pos)
        elif token.tok_type == TokenType.SWITCH:
            # 'switch' '(' <expression> ')' '{' {<labeled-statement>} '}'
            try:
                ast.add_child(self.__assert_token('switch', TokenType.SWITCH))
                ast.add_child(self.__assert_token(
                    '(', TokenType.LEFT_PARENTHESES))
                ast.add_child(self.__parse_expression())
                ast.add_child(self.__assert_token(
                    ')', TokenType.RIGHT_PARENTHESES))
                ast.add_child(self.__assert_token('{', TokenType.LEFT_BRACE))

                # {<labeled-statement>}
                while True:
                    token = self.__peek_token(suppress_exception=True)
                    if token is None:
                        raise ExpectedSymbol(self.__prev_token().ed_pos, '}')
                    if token.tok_type not in [TokenType.CASE, TokenType.DEFAULT]:
                        break
                    ast.add_child(self.__parse_labeled_statement())

                ast.add_child(self.__assert_token('}', TokenType.RIGHT_BRACE))

            except TokenIndexOutOfRange as e:
                print(e, file=sys.stderr)
                raise InvalidSwitchStatement(self.__prev_token().ed_pos)
        else:
            raise ExpectedSymbol(token.st_pos, 'if or switch')
        return ast

    def __parse_condition(self) -> Ast:
        """
        <condition> ::=
             <expression>[<relational-operator><expression>]
        """
        ast = Ast(AstType.CONDITION)

        # <expression>
        ast.add_child(self.__parse_expression())

        # [<relational-operator><expression>]
        token = self.__peek_token(suppress_exception=True)
        if token is not None and token.tok_type in TokenType.relations:
            ast.add_child(self.__parse_relational_operator())
            ast.add_child(self.__parse_expression())
        return ast

    def __parse_labeled_statement(self) -> Ast:
        """
        <labeled-statement> ::=
            'case' (<integer-literal>|<char-literal>) ':' <statement>
            |'default' ':' <statement>
        """
        ast = Ast(AstType.LABELED_STATEMENT)

        token = self.__peek_token()
        if token.tok_type == TokenType.CASE:
            ast.add_child(self.__assert_token('case', TokenType.CASE))

            token = self.__peek_token(suppress_exception=True)
            if token is None:
                raise ExpectedSymbol(
                    self.__prev_token().ed_pos, 'char or integer literal')
            if token.tok_type not in [TokenType.INTEGER_LITERAL, TokenType.CHAR_LITERAL]:
                raise ExpectedSymbol(
                    token.st_pos, 'char-literal or integer-literal')
            if token.tok_type == TokenType.INTEGER_LITERAL:
                ast.add_child(self.__parse_integer_literal())
            else:
                ast.add_child(self.__parse_char_literal())

            ast.add_child(self.__assert_token(':', TokenType.COLON))
            ast.add_child(self.__parse_statement())
        elif token.tok_type == TokenType.DEFAULT:
            ast.add_child(self.__assert_token('default', TokenType.DEFAULT))
            ast.add_child(self.__assert_token(':', TokenType.COLON))
            ast.add_child(self.__parse_statement())
        else:
            raise ExpectedSymbol(token.st_pos, '`case` or `default`')
        return ast

    def __assert_token(self, symbol: str, tok_type: TokenType) -> Ast:
        token = self.__next_token(suppress_exception=True)
        if token is None:
            raise ExpectedSymbol(self.__prev_token().ed_pos, symbol)
        if token.tok_type != tok_type:
            raise ExpectedSymbol(self.__prev_token().st_pos, symbol)
        return Ast(AstType.TOKEN, token)

    def __parse_loop_statement(self) -> Ast:
        """
        <loop-statement> ::=
            'while' '(' <condition> ')' <statement>
            |'do' <statement> 'while' '(' <condition> ')' ';'
            |'for' '('<for-init-statement> [<condition>]';' [<for-update-expression>]')' <statement>
        """
        ast = Ast(AstType.LOOP_STATEMENT)

        token = self.__peek_token()
        if token.tok_type == TokenType.WHILE:
            # 'while' '(' <condition> ')' <statement>
            ast.add_child(self.__assert_token('while', TokenType.WHILE))
            ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))
            ast.add_child(self.__parse_condition())
            ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
            ast.add_child(self.__parse_statement())
        elif token.tok_type == TokenType.DO:
            # 'do' <statement> 'while' '(' <condition> ')' ';'
            ast.add_child(self.__assert_token('do', TokenType.DO))
            ast.add_child(self.__parse_statement())
            ast.add_child(self.__assert_token('while', TokenType.WHILE))
            ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))
            ast.add_child(self.__parse_condition())
            ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
            ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        elif token.tok_type == TokenType.FOR:
            # 'for' '('<for-init-statement> [<condition>]';' [<for-update-expression>]')' <statement>
            ast.add_child(self.__assert_token('for', TokenType.FOR))
            ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))
            ast.add_child(self.__parse_for_init_statement())

            # [<condition>] ';'
            token = self.__peek_token(suppress_exception=True)
            if token is None:
                raise ExpectedSymbol(self.__prev_token().ed_pos, ';')
            if token.tok_type != TokenType.SEMICOLON:
                ast.add_child(self.__parse_condition())
            ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))

            # [<for-update-expression>]')' <statement>
            token = self.__peek_token(suppress_exception=True)
            if token is None:
                raise ExpectedSymbol(self.__prev_token().ed_pos, ')')
            if token.tok_type != TokenType.RIGHT_PARENTHESES:
                ast.add_child(self.__parse_for_update_expression())
            ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
            ast.add_child(self.__parse_statement())

        return ast

    def __parse_for_init_statement(self) -> Ast:
        """
        <for-init-statement> ::=
            [<assignment-expression>{','<assignment-expression>}]';'
        """
        ast = Ast(AstType.FOR_INIT_STATEMENT)

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise ExpectedSymbol(self.__prev_token().ed_pos, ';')

        if token.tok_type != TokenType.SEMICOLON:
            ast.add_child(self.__parse_assignment_expression())
            while True:
                token = self.__peek_token(suppress_exception=True)
                if token is None or token.tok_type != TokenType.COMMA:
                    break
                ast.add_child(self.__assert_token(',', TokenType.COMMA))
                ast.add_child(self.__parse_assignment_expression())

        ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        return ast

    def __parse_assignment_expression_or_function_call(self) -> Ast:
        self.__assert_token('identifier', TokenType.IDENTIFIER)
        token = self.__peek_token(suppress_exception=True)
        if token is None or token.tok_type not in [TokenType.LEFT_PARENTHESES, TokenType.ASSIGN]:
            raise ExpectedSymbol(self.__prev_token().ed_pos, '( or =')

        # (<assignment-expression>|<function-call>)
        self.__unread_token()
        if token.tok_type == TokenType.LEFT_PARENTHESES:
            return self.__parse_function_call()
        else:
            return self.__parse_assignment_expression()

    def __parse_for_update_expression(self) -> Ast:
        """
        <for-update-expression> ::=
            (<assignment-expression>|<function-call>){','(<assignment-expression>|<function-call>)}
        """
        ast = Ast(AstType.FOR_UPDATE_STATEMENT)

        ast.add_child(self.__parse_assignment_expression_or_function_call())
        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None or token.tok_type != TokenType.COMMA:
                break
            ast.add_child(self.__assert_token(',', TokenType.COMMA))
            ast.add_child(
                self.__parse_assignment_expression_or_function_call())
        return ast

    def __parse_jump_statement(self) -> Ast:
        """
        <jump-statement> ::=
            'break' ';'
            |'continue' ';'
            |<return-statement>
        """
        ast = Ast(AstType.JUMP_STATEMENT)

        token = self.__peek_token()
        if token.tok_type == TokenType.BREAK:
            ast.add_child(self.__assert_token('break', TokenType.BREAK))
            ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        elif token.tok_type == TokenType.CONTINUE:
            ast.add_child(self.__assert_token('continue', TokenType.CONTINUE))
            ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        else:
            ast.add_child(self.__parse_return_statement())

        return ast

    def __parse_return_statement(self) -> Ast:
        """
        <return-statement> ::= 'return' [<expression>] ';'
        """
        ast = Ast(AstType.RETURN_STATEMENT)

        ast.add_child(self.__assert_token('return', TokenType.RETURN))

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise ExpectedSymbol(self.__prev_token().ed_pos, ';')

        if token.tok_type != TokenType.SEMICOLON:
            ast.add_child(self.__parse_expression())
        ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))
        return ast

    def __parse_scan_statement(self) -> Ast:
        """
        <scan-statement> ::=
            'scan' '(' <identifier> ')' ';'
        """
        ast = Ast(AstType.SCAN_STATEMENT)

        ast.add_child(self.__assert_token('scan', TokenType.SCAN))
        ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))
        ast.add_child(self.__parse_identifier())
        ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
        ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))

        return ast

    def __parse_assignment_expression(self) -> Ast:
        """
        <assignment-expression> ::=
            <identifier><assignment-operator><expression>
        """
        ast = Ast(AstType.ASSIGNMENT_EXPRESSION)
        ast.add_child(self.__parse_identifier())
        ast.add_child(self.__parse_assignment_operator())
        ast.add_child(self.__parse_expression())
        return ast

    def __parse_print_statement(self) -> Ast:
        """
        <print-statement> ::=
            'print' '(' [<printable-list>] ')' ';'
        """
        ast = Ast(AstType.PRINT_STATEMENT)

        ast.add_child(self.__assert_token('print', TokenType.PRINT))
        ast.add_child(self.__assert_token('(', TokenType.LEFT_PARENTHESES))

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise ExpectedSymbol(self.__prev_token().ed_pos, ')')
        if token.tok_type != TokenType.RIGHT_PARENTHESES:
            ast.add_child(self.__parse_printable_list())

        ast.add_child(self.__assert_token(')', TokenType.RIGHT_PARENTHESES))
        ast.add_child(self.__assert_token(';', TokenType.SEMICOLON))

        return ast

    def __parse_printable_list(self) -> Ast:
        """
        <printable-list>  ::=
            <printable> {',' <printable>}
        """
        ast = Ast(AstType.PRINTABLE_LIST)

        ast.add_child(self.__parse_printable())
        while True:
            token = self.__peek_token(suppress_exception=True)
            if token is None or token.tok_type != TokenType.COMMA:
                break
            ast.add_child(self.__assert_token(',', TokenType.COMMA))
            ast.add_child(self.__parse_printable())
        return ast

    def __parse_printable(self) -> Ast:
        """
        <printable> ::=
            <expression> | <string-literal>
        """
        ast = Ast(AstType.PRINTABLE)

        token = self.__peek_token(suppress_exception=True)
        if token is None:
            raise ExpectedSymbol(self.__prev_token().ed_pos,
                                 'string-literal or identifier')

        if token.tok_type == TokenType.STR_LITERAL:
            ast.add_child(self.__parse_str_literal())
        else:
            ast.add_child(self.__parse_expression())
        return ast

    def __eof(self):
        return self.tok_idx == len(self.tokens) - 1

    def __next_token(self, suppress_exception: bool = False) -> typing.Union[Token, None]:
        token = self.__peek_token(suppress_exception=suppress_exception)
        self.tok_idx += 1
        debug(f'[next token] {token}')
        return token

    def __peek_token(self, suppress_exception: bool = False) -> typing.Union[Token, None]:
        if self.tok_idx == len(self.tokens):
            if suppress_exception:
                return None
            else:
                raise TokenIndexOutOfRange('No more token to read')
        return self.tokens[self.tok_idx]

    def __unread_token(self):
        if self.tok_idx == 0:
            raise TokenIndexOutOfRange('Cannot unread token beyond 0')
        self.tok_idx -= 1
        debug(f'[unread token] {self.tokens[self.tok_idx]}')

    def __current_pos(self) -> tuple:
        return self.tokens[self.tok_idx].st_pos

    def __rollback_idx(self, idx: int):
        if idx < 0 or idx >= len(self.tokens):
            raise TokenIndexOutOfRange(
                f'Cannot rollback to token index {idx}, which is out of range')
        self.tok_idx = idx

    def __prev_token(self) -> Token:
        if self.tok_idx <= 1:
            raise TokenIndexOutOfRange(
                f'cannot read previous token of first token')
        return self.tokens[self.tok_idx - 2]
