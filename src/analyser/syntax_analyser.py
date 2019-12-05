from analyser.parser import C0ASTParser, Ast
from analyser.ast import Ast
from analyser.symbol_table import SymbolTable
from analyser.pcode import PCode
from tokenizer import Token
from typing import List


class Analyser(object):
    def __init__(self, tokens: List[Token]):
        self.ast = C0ASTParser(tokens).parse()
        self.symbol_table = SymbolTable()
        self.instructions: List[PCode] = []
        self.generated = False

    def generate_instructions(self):
        if not self.generated:
            self.__generate()
            self.generated = True
        return self.instructions

    def __generate(self):
        pass

    def __analyse_c0(self, ast: Ast):
        """
        <C0-program> ::=
            {<variable-declaration>}{<function-definition>}
        """
        pass

    def __analyse_variable_declaration(self, ast: Ast):
        """
        <variable-declaration> ::=
            [<const-qualifier>]<type-specifier><init-declarator-list>';'
        """
        pass

    def __analyse_function_definition(self, ast: Ast):
        """
        <function-definition> ::=
            <type-specifier><identifier><parameter-clause><compound-statement>
        """
        pass

    def __analyse_const_qualifier(self, ast: Ast):
        """
        <const-qualifier>        ::= 'const'
        """
        pass

    def __analyse_type_specifier(self, ast: Ast):
        """
        <type-specifier>         ::= <simple-type-specifier>
        """
        pass

    def __analyse_simple_type_specifier(self, ast: Ast):
        """
        <simple-type-specifier>  ::= 'void'|'int'|'char'|'double'
        """
        pass

    def __analyse_init_declarator_list(self, ast: Ast):
        """
        <init-declarator-list> ::=
            <init-declarator>{','<init-declarator>}
        """
        pass

    def __analyse_init_declarator(self, ast: Ast):
        """
        <init-declarator> ::=
            <identifier>[<initializer>]
        """
        pass

    def __analyse_initializer(self, ast: Ast):
        """
        <initializer> ::=
            '='<expression>
        """
        pass

    def __analyse_expression(self, ast: Ast):
        """
        <expression> ::=
            <additive-expression>
        """
        pass

    def __analyse_additive_expression(self, ast: Ast):
        """
        <additive-expression> ::=
            <multiplicative-expression>{<additive-operator><multiplicative-expression>}
        """
        pass

    def __analyse_multiplicative_expression(self, ast: Ast):
        """
        <multiplicative-expression> ::=
            <cast-expression>{<multiplicative-operator><cast-expression>}
        """
        pass

    def __analyse_cast_expression(self, ast: Ast):
        """
        <cast-expression> ::=
            {'('<type-specifier>')'}<unary-expression>
        """
        pass

    def __analyse_unary_expression(self, ast: Ast):
        """
        <unary-expression> ::=
            [<unary-operator>]<primary-expression>
        """
        pass

    def __analyse_primary_expression(self, ast: Ast):
        """
        <primary-expression> ::=
            '('<expression>')'
            |<identifier>
            |<integer-literal>
            |<char-literal>
            |<floating-literal>
            |<function-call>
        """
        pass

    def __analyse_function_call(self, ast: Ast):
        """
        <function-call> ::=
            <identifier> '(' [<expression-list>] ')'
        """
        pass

    def __analyse_expression_list(self, ast: Ast):
        """
        <expression-list> ::=
            <expression>{','<expression>}
        """
        pass

    def __analyse_parameter_clause(self, ast: Ast):
        """
        <parameter-clause> ::=
            '(' [<parameter-declaration-list>] ')'
        """
        pass

    def __analyse_parameter_declaration_list(self, ast: Ast):
        """
        <parameter-declaration-list> ::=
            <parameter-declaration>{','<parameter-declaration>}
        """
        pass

    def __analyse_parameter_declaration(self, ast: Ast):
        """
        <parameter-declaration> ::=
            [<const-qualifier>]<type-specifier><identifier>
        """
        pass

    def __analyse_compound_statement(self, ast: Ast):
        """
        <compound-statement> ::=
            '{' {<variable-declaration>} <statement-seq> '}'
        """
        pass

    def __analyse_statement_seq(self, ast: Ast):
        """
        <statement-seq> ::=
            {<statement>}
        """
        pass

    def __analyse_statement(self, ast: Ast):
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
        pass

    def __analyse_condition_statement(self, ast: Ast):
        """
        <condition-statement> ::=
            'if' '(' <condition> ')' <statement> ['else' <statement>]
            |'switch' '(' <expression> ')' '{' {<labeled-statement>} '}'
        """
        pass

    def __analyse_condition(self, ast: Ast):
        """
        <condition> ::=
            <expression>[<relational-operator><expression>]
        """
        pass

    def __analyse_labeled_statement(self, ast: Ast):
        """
        <labeled-statement> ::=
            'case' (<integer-literal>|<char-literal>) ':' <statement>
            |'default' ':' <statement>
        """
        pass

    def __analyse_loop_statement(self, ast: Ast):
        """
        <loop-statement> ::=
            'while' '(' <condition> ')' <statement>
            |'do' <statement> 'while' '(' <condition> ')' ';'
            |'for' '('<for-init-statement> [<condition>]';' [<for-update-expression>]')' <statement>
        """
        pass

    def __analyse_for_init_statement(self, ast: Ast):
        """
        <for-init-statement> ::=
            [<assignment-expression>{','<assignment-expression>}]';'
        """
        pass

    def __analyse_assignment_expression_or_function_call(self, ast: Ast):
        pass

    def __analyse_for_update_expression(self, ast: Ast):
        """
        <for-update-expression> ::=
            (<assignment-expression>|<function-call>){','(<assignment-expression>|<function-call>)}
        """
        pass

    def __analyse_jump_statement(self, ast: Ast):
        """
        <jump-statement> ::=
            'break' ';'
            |'continue' ';'
            |<return-statement>
        """
        pass

    def __analyse_return_statement(self, ast: Ast):
        """
        <return-statement> ::= 'return' [<expression>] ';'
        """
        pass

    def __analyse_scan_statement(self, ast: Ast):
        """
        <scan-statement> ::=
            'scan' '(' <identifier> ')' ';'
        """
        pass

    def __analyse_assignment_expression(self, ast: Ast):
        """
        <assignment-expression> ::=
            <identifier><assignment-operator><expression>
        """
        pass

    def __analyse_print_statement(self, ast: Ast):
        """
        <print-statement> ::=
            'print' '(' [<printable-list>] ')' ';'
        """
        pass

    def __analyse_printable_list(self, ast: Ast):
        """
        <printable-list>  ::=
            <printable> {',' <printable>}
        """
        pass

    def __analyse_printable(self, ast: Ast):
        """
        <printable> ::=
            <expression> | <string-literal>
        """
        pass

    def __analyse_identifier(self, ast: Ast):
        pass

    def __analyse_unary_operator(self, ast: Ast):
        """
        <unary-operator>          ::= '+' | '-'
        """
        pass

    def __analyse_additive_operator(self, ast: Ast):
        """
        <additive-operator>       ::= '+' | '-'
        """
        pass

    def __analyse_multiplicative_operator(self, ast: Ast):
        """
        <multiplicative-operator> ::= '*' | '/'
        """
        pass

    def __analyse_relational_operator(self, ast: Ast):
        """
        <relational-operator>     ::= '<' | '<=' | '>' | '>=' | '!=' | '=='
        """
        pass

    def __analyse_assignment_operator(self, ast: Ast):
        """
        <assignment-operator>     ::= '='
        """
        pass

    def __analyse_integer_literal(self, ast: Ast):
        pass

    def __analyse_char_literal(self, ast: Ast):
        pass

    def __analyse_float_literal(self, ast: Ast):
        pass

    def __analyse_str_literal(self, ast: Ast):
        pass
