from analyser.parser import C0ASTParser, AstType
from analyser.ast import Ast
from analyser.symbol_table import SymbolTable, SymbolAttrs
from tokenizer import Token, TokenType
from elf.pcode import PCode
from elf.elf import ELF, Constant
from exception.analyser_exceptions import *
from typing import List, Tuple, Any


def assert_ast_type(ast: Ast, assertion_type: str):
    if ast.type != assertion_type:
        ast.draw()
        assert False, f'Expected ast of type {assertion_type}, but received {ast.type}'


def get_pos(ast: Ast):
    if ast.token is not None:
        return ast.token.st_pos
    return get_pos(ast.first_child())


class Analyser(object):
    def __init__(self, tokens: List[Token]):
        self.c0_ast = C0ASTParser(tokens).parse()
        self.symbol_table = SymbolTable()
        self.elf = ELF()
        self.generated = False

    def generate(self):
        if not self.generated:
            self.__generate()
            self.generated = True
        return self.elf

    def add_inst(self, inst_type: str, *ops, at_idx: int = None):
        instructions = self.elf.current_instructions()
        if at_idx is None:
            instructions.append(PCode(inst_type, *ops))
        else:
            instructions.insert(at_idx, PCode(inst_type, *ops))

    def __generate(self):
        self.__analyse_c0(self.c0_ast)

    def __analyse_c0(self, ast: Ast):
        """
        <C0-program> ::=
            {<variable-declaration>}{<function-definition>}
        """
        assert_ast_type(ast, AstType.C0)

        self.symbol_table.enter_level()
        for child in ast.children:
            if child.type == AstType.VARIABLE_DECLARATION:
                self.__analyse_variable_declaration(child)
            else:
                self.__analyse_function_definition(child)

        if not self.elf.has_function("main"):
            raise MissingMain(get_pos(ast))

    def __analyse_variable_declaration(self, ast: Ast):
        """
        <variable-declaration> ::=
            [<const-qualifier>]<type-specifier><init-declarator-list>';'
        """
        assert_ast_type(ast, AstType.VARIABLE_DECLARATION)

        constness = (ast.first_child().type == AstType.CONST_QUALIFIER)
        idx = 1 if constness else 0
        type_ = self.__analyse_type_specifier(ast.children[idx])
        if type_ == TokenType.VOID:
            raise VoidVariableException(get_pos(ast.children[idx]))

        type_info = {
            SymbolAttrs.CONSTNESS: constness,
            SymbolAttrs.TYPE: type_
        }
        self.__analyse_init_declarator_list(ast.children[-2], type_info)

    def __analyse_function_definition(self, ast: Ast):
        """
        <function-definition> ::=
            <type-specifier><identifier><parameter-clause><compound-statement>
        """
        assert_ast_type(ast, AstType.FUNCTION_DEFINITION)

        return_type = self.__analyse_type_specifier(ast.first_child())
        func_name = self.__analyse_identifier(ast.children[1])
        if self.elf.has_function(func_name):
            raise FunctionRedefinitionException(
                get_pos(ast.children[1]), func_name)
        idx = self.elf.add_constant(Constant.STR, func_name)

        # put parameters and function body in a same new scope
        self.symbol_table.enter_level(new_stack=True)

        # [type_of_param_0, ..., type_of_param_k]
        params_info = self.__analyse_parameter_clause(ast.children[2])
        self.elf.add_function(return_type, func_name, idx, params_info)

        # {'return': count_of_return_statement, ..., 'if': count_of_if_statement}
        statements_info = self.__analyse_compound_statement(
            ast.children[3], enter_level=False)

        if 'return' not in statements_info and return_type != TokenType.VOID:
            print(statements_info)
            raise NoReturnValueForNotVoidFunction(get_pos(ast.children[3]))

        # Bad code, but I don't want to cost too much on this `control-flow` tracing work
        # which is definitely too complicated.
        if return_type == TokenType.VOID:
            self.add_inst(PCode.RET)
        elif return_type == TokenType.DOUBLE:
            self.add_inst(PCode.IPUSH, 0)
            self.add_inst(PCode.I2D)
            self.add_inst(PCode.DRET)
        else:
            self.add_inst(PCode.IPUSH, 0)
            self.add_inst(PCode.IRET)

    def __analyse_type_specifier(self, ast: Ast) -> str:
        """
        <type-specifier>         ::= <simple-type-specifier>
        Return `TokenType` of corresponding type
        """
        assert_ast_type(ast, AstType.TYPE_SPECIFIER)
        return self.__analyse_simple_type_specifier(ast.first_child())

    @staticmethod
    def __analyse_simple_type_specifier(ast: Ast):
        """
        <simple-type-specifier>  ::= 'void'|'int'|'char'|'double'
        """
        assert_ast_type(ast, AstType.SIMPLE_TYPE_SPECIFIER)

        type_ = ast.first_child().token.tok_type
        assert type_ in TokenType.types, 'Type error, it should be detected before analysing'
        return type_

    def __analyse_init_declarator_list(self, ast: Ast, type_info: dict):
        """
        <init-declarator-list> ::=
            <init-declarator>{','<init-declarator>}
        """
        assert_ast_type(ast, AstType.INIT_DECLARATOR_LIST)

        for child in ast.children:
            if child.type == AstType.INIT_DECLARATOR:
                self.__analyse_init_declarator(child, type_info)

    def convert_from_type_to_type(self, to_type: str, from_type: str, to_pos: tuple, from_pos: tuple,
                                  at_idx: int = None):
        """
        Convert value at the top of stack from `from_type` to `to_type`.
        Also help to check whether the types involved are supported.
        """
        if from_type == TokenType.VOID:
            raise VoidTypeCalculationNotSupported(from_pos)
        elif from_type not in TokenType.types:
            raise UnknownVariableType(to_pos, to_type)

        if to_type == TokenType.VOID:
            raise VoidTypeCalculationNotSupported(to_pos)
        elif to_type not in TokenType.types:
            raise UnknownVariableType(to_pos, to_type)

        if from_type == to_type:
            return

        if from_type == TokenType.INT:
            if to_type == TokenType.CHAR:
                self.add_inst(PCode.I2C, at_idx=at_idx)
            else:
                assert to_type == TokenType.DOUBLE
                self.add_inst(PCode.I2D, at_idx=at_idx)

        elif from_type == TokenType.CHAR:
            if to_type == TokenType.INT:
                return
            else:
                assert to_type == TokenType.DOUBLE
                self.add_inst(PCode.I2D, at_idx=at_idx)

        else:
            assert from_type == TokenType.DOUBLE
            if to_type == TokenType.INT:
                self.add_inst(PCode.D2I, at_idx=at_idx)
            else:
                assert to_type == TokenType.CHAR
                if at_idx is not None:
                    self.add_inst(PCode.D2I, at_idx=at_idx)
                    self.add_inst(PCode.I2C, at_idx=at_idx + 1)
                else:
                    self.add_inst(PCode.D2I)
                    self.add_inst(PCode.I2C)

    def __analyse_init_declarator(self, ast: Ast, type_info: dict):
        """
        <init-declarator> ::=
            <identifier>[<initializer>]
        """
        assert_ast_type(ast, AstType.INIT_DECLARATOR)

        symbol_name = self.__analyse_identifier(ast.first_child())
        if symbol_name in self.symbol_table.current_level():
            raise DuplicateSymbol(get_pos(ast.first_child()), symbol_name)
        self.symbol_table.add_symbol(symbol_name, type_info.copy())

        symbol_type = self.symbol_table.get_type(symbol_name)
        symbol_size = self.symbol_table.get_size(symbol_name)
        symbol_offset = self.symbol_table.get_offset(symbol_name)
        symbol_pos = get_pos(ast.first_child())

        # allocate space on stack for variable
        self.add_inst(PCode.SNEW, symbol_size)

        if len(ast.children) == 1:
            # const variable must be initialized
            if type_info[SymbolAttrs.CONSTNESS]:
                raise ConstantNotInitialized(get_pos(ast.first_child()))
        else:
            # load absolute address of symbol
            self.add_inst(PCode.LOADA, *symbol_offset)

            type_, _ = self.__analyse_initializer(ast.children[1])
            if type_ != symbol_type:
                self.convert_from_type_to_type(to_type=symbol_type,
                                               from_type=type_,
                                               to_pos=symbol_pos,
                                               from_pos=get_pos(ast.children[1]))
            # store (new) value
            if symbol_type in [TokenType.INT, TokenType.CHAR]:
                self.add_inst(PCode.ISTORE)
            elif symbol_type == TokenType.DOUBLE:
                self.add_inst(PCode.DSTORE)
            else:
                raise UnknownVariableType(get_pos(ast.children[1]), type_)

    def __analyse_initializer(self, ast: Ast) -> Tuple[str, Any]:
        """
        <initializer> ::=
            '='<expression>
        After return, left the value be on the top of current stack
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time
                value_type is not VOID
        """
        assert_ast_type(ast, AstType.INITIALIZER)

        expr = ast.children[1]
        type_, value = self.__analyse_expression(expr)
        if type_ == TokenType.VOID:
            raise VoidTypeCalculationNotSupported(get_pos(expr))
        return type_, value

    def __analyse_expression(self, ast: Ast) -> Tuple[str, Any]:
        """
        <expression> ::=
            <additive-expression>
        After return, if value_type is not `VOID` left the value be on the top of current stack
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time,
                value_type is `VOID` iff expression is consisted of single void function call,
                `CHAR` iff expression is consisted of single char-literal or char-variable,
                `INT` or `DOUBLE` (`CHAR` promoted to `INT`) for any other case
        """
        assert_ast_type(ast, AstType.EXPRESSION)

        add_expr = ast.first_child()
        expr_type, _ = self.__analyse_additive_expression(add_expr)
        return expr_type, None

    def __analyse_additive_expression(self, ast: Ast) -> Tuple[str, Any]:
        """
        <additive-expression> ::=
            <multiplicative-expression>{<additive-operator><multiplicative-expression>}
        After return, if value_type is not `VOID` left the value be on the top of current stack
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time,
                value_type is `VOID` iff expression is consisted of single void function call,
                `CHAR` iff expression is consisted of single char-literal or char-variable,
                `INT` or `DOUBLE` (`CHAR` promoted to `INT`) for any other case
        """
        assert_ast_type(ast, AstType.ADDITIVE_EXPRESSION)

        mul_expr = ast.first_child()
        l_type, _ = self.__analyse_multiplicative_expression(mul_expr)
        instruction_idx = self.elf.next_inst_idx()

        for op, mul_expr in zip(ast.children[1::2], ast.children[2::2]):
            op = self.__analyse_additive_operator(op)
            r_type, _ = self.__analyse_multiplicative_expression(mul_expr)

            if l_type == TokenType.VOID or r_type == TokenType.VOID:
                raise VoidTypeCalculationNotSupported(get_pos(mul_expr))
            if l_type == TokenType.CHAR:
                l_type = TokenType.INT
            if r_type == TokenType.CHAR:
                r_type = TokenType.INT

            # make l_type and r_type fit
            if l_type != r_type:
                # `int` op `double`
                if l_type == TokenType.INT:
                    l_type = TokenType.DOUBLE
                    self.add_inst(PCode.I2D, at_idx=instruction_idx)
                # `double` op `int`
                elif l_type == TokenType.DOUBLE:
                    self.add_inst(PCode.I2D)

            # decide inst based on `op` and `l_type`
            if op == TokenType.ADD:
                if l_type == TokenType.DOUBLE:
                    self.add_inst(PCode.DADD)
                else:
                    self.add_inst(PCode.IADD)
            else:
                if l_type == TokenType.DOUBLE:
                    self.add_inst(PCode.DSUB)
                else:
                    self.add_inst(PCode.ISUB)
            instruction_idx = self.elf.next_inst_idx()

        return l_type, None

    def __analyse_multiplicative_expression(self, ast: Ast) -> Tuple[str, Any]:
        """
        <multiplicative-expression> ::=
            <cast-expression>{<multiplicative-operator><cast-expression>}
        After return, if value_type is not `VOID` left the value be on the top of current stack
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time,
                value_type is `VOID` iff expression is consisted of single void function call,
                `CHAR` iff expression is consisted of single char-literal or char-variable or casted,
                `INT` or `DOUBLE` (`CHAR` promoted to `INT`) for any other case
        """
        assert_ast_type(ast, AstType.MULTIPLICATIVE_EXPRESSION)

        cast_expr = ast.first_child()
        l_type, _ = self.__analyse_cast_expression(cast_expr)
        instruction_idx = self.elf.next_inst_idx()

        for op, cast_expr in zip(ast.children[1::2], ast.children[2::2]):
            op = self.__analyse_multiplicative_operator(op)
            r_type, _ = self.__analyse_cast_expression(cast_expr)

            if l_type == TokenType.VOID or r_type == TokenType.VOID:
                raise VoidTypeCalculationNotSupported(get_pos(cast_expr))
            if l_type == TokenType.CHAR:
                l_type = TokenType.INT
            if r_type == TokenType.CHAR:
                r_type = TokenType.INT

            # make l_type and r_type fit
            if l_type != r_type:
                # `int` op `double`
                if l_type == TokenType.INT:
                    l_type = TokenType.DOUBLE
                    self.add_inst(PCode.I2D, at_idx=instruction_idx)
                # `double` op `int`
                elif l_type == TokenType.DOUBLE:
                    self.add_inst(PCode.I2D)

            # decide inst based on `op` and `l_type`
            if op == TokenType.MUL:
                if l_type == TokenType.DOUBLE:
                    self.add_inst(PCode.DMUL)
                else:
                    self.add_inst(PCode.IMUL)
            else:
                if l_type == TokenType.DOUBLE:
                    self.add_inst(PCode.DDIV)
                else:
                    self.add_inst(PCode.IDIV)
            instruction_idx = self.elf.next_inst_idx()

        return l_type, None

    def __analyse_cast_expression(self, ast: Ast) -> Tuple[str, Any]:
        """
        <cast-expression> ::=
            {'('<type-specifier>')'}<unary-expression>
        After return, if value_type is not `VOID` left the value be on the top of current stack
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time,
                value_type is `VOID` iff expression is consisted of single void function call,
                `CHAR` iff expression is consisted of single char-literal or char-variable or casted,
                `INT` or `DOUBLE` (`CHAR` promoted to `INT`) for any other case
        """
        assert_ast_type(ast, AstType.CAST_EXPRESSION)

        unary_expr = ast.children[-1]
        from_type, _ = self.__analyse_unary_expression(unary_expr)
        from_pos = get_pos(unary_expr)

        types = [x for x in ast.children if x.type == AstType.TYPE_SPECIFIER]
        types.reverse()

        for type_specifier in types:
            to_pos = get_pos(type_specifier)
            to_type = self.__analyse_type_specifier(type_specifier)
            self.convert_from_type_to_type(to_type=to_type,
                                           from_type=from_type,
                                           to_pos=to_pos,
                                           from_pos=from_pos)
            from_pos = to_pos
            from_type = to_type

        return from_type, None

    def __analyse_unary_expression(self, ast: Ast) -> Tuple[str, Any]:
        """
        <unary-expression> ::=
            [<unary-operator>]<primary-expression>
        After return, if value_type is not `VOID` left the value be on the top of current stack
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time,
                value_type is `VOID` iff expression is consisted of single void function call,
                `CHAR` iff expression is consisted of single char-literal or char-variable,
                `INT` or `DOUBLE` (`CHAR` promoted to `INT`) for any other case
        """
        assert_ast_type(ast, AstType.UNARY_EXPRESSION)

        primary_expr = ast.children[-1]
        type_, _ = self.__analyse_primary_expression(primary_expr)

        if len(ast.children) == 2:
            if type_ == TokenType.VOID:
                raise VoidTypeCalculationNotSupported(get_pos(primary_expr))

            # `char` must be converted to `int` before any calculation
            if type_ == TokenType.CHAR:
                type_ = TokenType.INT

            op = self.__analyse_unary_operator(ast.first_child())
            if op == TokenType.SUB:
                if type_ == TokenType.DOUBLE:
                    self.add_inst(PCode.DNEG)
                else:
                    # INT or CHAR
                    self.add_inst(PCode.INEG)
            else:
                assert op == TokenType.ADD
        return type_, None

    def __analyse_primary_expression(self, ast: Ast) -> Tuple[str, Any]:
        """
        <primary-expression> ::=
            '('<expression>')'
            |<identifier>
            |<integer-literal>
            |<char-literal>
            |<floating-literal>
            |<function-call>
        After return, if value_type is not `VOID` left the value be on the top of current stack
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time,
                value_type is `VOID` iff expression is consisted of single void function call,
                `CHAR` iff expression is consisted of single char-literal or char-variable,
                `INT` or `DOUBLE` (`CHAR` promoted to `INT`) for any other case
        """
        assert_ast_type(ast, AstType.PRIMARY_EXPRESSION)

        child_type = ast.first_child().type
        if child_type == AstType.TOKEN:
            return self.__analyse_expression(ast.children[1])

        elif child_type == AstType.IDENTIFIER:
            symbol_name = self.__analyse_identifier(ast.first_child())
            if symbol_name not in self.symbol_table:
                raise UndefinedSymbol(get_pos(ast.first_child()), symbol_name)
            symbol_offset = self.symbol_table.get_offset(symbol_name)
            symbol_type = self.symbol_table.get_type(symbol_name)
            self.add_inst(PCode.LOADA, *symbol_offset)
            if symbol_type in [TokenType.INT, TokenType.CHAR]:
                self.add_inst(PCode.ILOAD)
            elif symbol_type == TokenType.DOUBLE:
                self.add_inst(PCode.DLOAD)
            return self.symbol_table.get_type(symbol_name), None

        elif child_type == AstType.INTEGER_LITERAL:
            value = self.__analyse_integer_literal(ast.first_child())
            self.add_inst(PCode.IPUSH, value)
            return TokenType.INT, value

        elif child_type == AstType.CHAR_LITERAL:
            value = self.__analyse_char_literal(ast.first_child())
            value = ord(value)
            self.add_inst(PCode.BIPUSH, value)
            return TokenType.CHAR, value

        elif child_type == AstType.FLOAT_LITERAL:
            value = self.__analyse_float_literal(ast.first_child())
            idx = self.elf.add_constant(Constant.DOUBLE, value)
            self.add_inst(PCode.LOADC, idx)
            return TokenType.DOUBLE, value

        else:
            assert child_type == AstType.FUNCTION_CALL, 'Unexpected error, invalid primary_expr'
            return self.__analyse_function_call(ast.first_child())

    def __analyse_function_call(self, ast: Ast) -> Tuple[str, Any]:
        """
        <function-call> ::=
            <identifier> '(' [<expression-list>] ')'
        Return: pair of (value_type, value)
                value can be None if not accessible at compiling time,
                value_type is `INT` or `DOUBLE` or `VOID` (`CHAR` promoted to `INT`)
        """
        assert_ast_type(ast, AstType.FUNCTION_CALL)

        func_name = self.__analyse_identifier(ast.first_child())
        if not self.elf.has_function(func_name):
            if func_name in self.symbol_table:
                raise NotCallingFunction(get_pos(ast.first_child()), func_name)
            else:
                raise FunctionNotDefined(get_pos(ast.first_child()), func_name)

        # prepare parameters, put values on stack-top from left to right
        params_info = self.elf.function_params_info(func_name)
        arg_count = 0
        if ast.children[2].type == AstType.EXPRESSION_LIST:
            arg_count = self.__analyse_expression_list(
                ast.children[2], params_info)

        param_count = self.elf.function_param_count(func_name)
        if arg_count != param_count:
            raise ArgumentsNumberNotMatchException(
                get_pos(ast.children[1]), param_count, arg_count)

        func_id = self.elf.function_index(func_name)
        self.add_inst(PCode.CALL, func_id)
        return self.elf.function_return_type(func_name), None

    def __analyse_expression_list(self, ast: Ast, params_info: List[str]) -> int:
        """
        <expression-list> ::=
            <expression>{','<expression>}
        params_info: List of types of parameters
        Return number of argument passed to callee
        """
        assert_ast_type(ast, AstType.EXPRESSION_LIST)

        arguments = [x for x in ast.children if x.type == AstType.EXPRESSION]
        for param_type, arg in zip(params_info, arguments):
            arg_type, _ = self.__analyse_expression(arg)
            # print(f'{arg_type} to {param_type}')
            if arg_type != param_type:
                # NOTE: better send a warning here
                self.convert_from_type_to_type(to_type=param_type,
                                               from_type=arg_type,
                                               to_pos=get_pos(arg),
                                               from_pos=get_pos(arg))
        return len(arguments)

    def __analyse_parameter_clause(self, ast: Ast) -> list:
        """
        <parameter-clause> ::=
            '(' [<parameter-declaration-list>] ')'
        Return types of parameters defined
        """
        assert_ast_type(ast, AstType.PARAMETER_CLAUSE)

        if ast.children[1].type == AstType.PARAMETER_DECLARATION_LIST:
            return self.__analyse_parameter_declaration_list(ast.children[1])
        return []

    def __analyse_parameter_declaration_list(self, ast: Ast) -> list:
        """
        <parameter-declaration-list> ::=
            <parameter-declaration>{','<parameter-declaration>}
        Return types of parameters defined
        """
        assert_ast_type(ast, AstType.PARAMETER_DECLARATION_LIST)

        # parameters: value in reversed order, last param at stack-top
        params = [x for x in ast.children if x.type ==
                  AstType.PARAMETER_DECLARATION]
        params_info: List[str] = []
        for param in params:
            params_info.append(self.__analyse_parameter_declaration(param))
        return params_info

    def __analyse_parameter_declaration(self, ast: Ast) -> str:
        """
        <parameter-declaration> ::=
            [<const-qualifier>]<type-specifier><identifier>
        Return type of parameter
        """
        assert_ast_type(ast, AstType.PARAMETER_DECLARATION)

        constness = (ast.first_child().type == AstType.CONST_QUALIFIER)
        idx = 1 if constness else 0

        type_ = self.__analyse_type_specifier(ast.children[idx])
        if type_ == TokenType.VOID:
            raise VoidVariableException(get_pos(ast.children[idx]))
        type_info = {
            SymbolAttrs.CONSTNESS: constness,
            SymbolAttrs.TYPE: type_
        }

        # declare params just like declare local variable, the only
        # difference is parameters are already initialized
        symbol_name = self.__analyse_identifier(ast.children[-1])

        # this will update the offset correctly automatically
        self.symbol_table.add_symbol(symbol_name, type_info)

        return type_

    def __analyse_compound_statement(self, ast: Ast, enter_level: bool = True) -> dict:
        """
        <compound-statement> ::=
            '{' {<variable-declaration>} <statement-seq> '}'
        Return statement statics, e.g. how many `return`s, `while`s
        """
        assert_ast_type(ast, AstType.COMPOUND_STATEMENT)

        # `False` only if this is a function body
        if enter_level:
            self.symbol_table.enter_level()

        variable_declarations = [
            x for x in ast.children if x.type == AstType.VARIABLE_DECLARATION]
        for var_decl in variable_declarations:
            self.__analyse_variable_declaration(var_decl)
        info = self.__analyse_statement_seq(ast.children[-2])

        self.symbol_table.exit_level()
        return info

    def __analyse_statement_seq(self, ast: Ast) -> dict:
        """
        <statement-seq> ::=
            {<statement>}
        Return statement statics, e.g. how many `return`s, `while`s
        """
        assert_ast_type(ast, AstType.STATEMENT_SEQ)

        info = {}
        for statement in ast.children:
            statement_info = self.__analyse_statement(statement)
            info = {**info, **statement_info}
        return info

    def __analyse_statement(self, ast: Ast) -> dict:
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
        Return statement statics, e.g. how many `return`s, `while`s
        """
        assert_ast_type(ast, AstType.STATEMENT)

        child_type = ast.first_child().type
        if child_type == AstType.COMPOUND_STATEMENT:
            return self.__analyse_compound_statement(ast.first_child())

        elif child_type == AstType.CONDITION_STATEMENT:
            return self.__analyse_condition_statement(ast.first_child())

        elif child_type == AstType.LOOP_STATEMENT:
            return self.__analyse_loop_statement(ast.first_child())

        elif child_type == AstType.JUMP_STATEMENT:
            return self.__analyse_jump_statement(ast.first_child())

        elif child_type == AstType.PRINT_STATEMENT:
            self.__analyse_print_statement(ast.first_child())
            return {'print': 1}

        elif child_type == AstType.SCAN_STATEMENT:
            self.__analyse_scan_statement(ast.first_child())
            return {'scan': 1}

        elif child_type == AstType.ASSIGNMENT_EXPRESSION:
            self.__analyse_assignment_expression(ast.first_child())

        elif child_type == AstType.FUNCTION_CALL:
            self.__analyse_function_call(ast.first_child())

        else:
            assert child_type == AstType.TOKEN, f'Expected `;`, got {child_type}'
        return {}

    def __analyse_condition_statement(self, ast: Ast) -> dict:
        """
        <condition-statement> ::=
            'if' '(' <condition> ')' <statement> ['else' <statement>]
            |'switch' '(' <expression> ')' '{' {<labeled-statement>} '}'
        Return statement statics, e.g. how many `return`s, `while`s
        """
        assert_ast_type(ast, AstType.CONDITION_STATEMENT)

        # NOTE: only handle `if`
        statements_info = {}
        first_token = ast.first_child().token
        if first_token.tok_type == TokenType.IF:
            condition = ast.children[2]
            if_stat = ast.children[4]

            j_instruction = self.__analyse_condition(condition)
            j_instruction_idx = self.elf.next_inst_idx()
            self.add_inst(j_instruction, 0)
            statements_info = {**statements_info,
                               **self.__analyse_statement(if_stat)}

            # if-else
            if ast.children[-2].token.tok_type == TokenType.ELSE:
                jmp_instruction_idx = self.elf.next_inst_idx()
                self.add_inst(PCode.JMP, 0)

                else_stat = ast.children[-1]
                else_start_instruction_index = self.elf.next_inst_idx()
                statements_info = {**statements_info,
                                   **self.__analyse_statement(else_stat)}
                instruction_index_after_else = self.elf.next_inst_idx()

                j_offset = else_start_instruction_index
                jmp_offset = instruction_index_after_else
                self.elf.update_instruction_at(j_instruction_idx, j_offset)
                self.elf.update_instruction_at(jmp_instruction_idx, jmp_offset)
            # naive if
            else:
                instruction_index_after_if = self.elf.next_inst_idx()
                j_offset = instruction_index_after_if
                self.elf.update_instruction_at(j_instruction_idx, j_offset)
            return statements_info
        else:
            raise NotSupportedFeature(get_pos(ast), 'switch statement')

    def __analyse_condition(self, ast: Ast) -> str:
        """
        <condition> ::=
            <expression>[<relational-operator><expression>]
        After return, left the condition-value of the top of stack,
        value must be of type `INT`, while `0` for `False`, otherwise `True`
        Return: corresponding `jump` instruction needed, `JE` for `!=`, `JL` for `>=`
            i.e. the jump instruction that perform jumping when condition is `False`
        """
        assert_ast_type(ast, AstType.CONDITION)

        l_type, _ = self.__analyse_expression(ast.first_child())
        if l_type == TokenType.VOID:
            raise VoidTypeCalculationNotSupported(get_pos(ast.first_child()))
        instruction_idx = self.elf.next_inst_idx()

        if len(ast.children) == 1:
            if l_type == TokenType.DOUBLE:
                self.add_inst(PCode.D2I)
            return PCode.JE
        else:
            cmp_op = self.__analyse_relational_operator(ast.children[1])
            r_type, _ = self.__analyse_expression(ast.children[-1])
            if r_type == TokenType.VOID:
                raise VoidTypeCalculationNotSupported(
                    get_pos(ast.children[-1]))
            if l_type == TokenType.CHAR:
                l_type = TokenType.INT
            if r_type == TokenType.CHAR:
                r_type = TokenType.INT

            if r_type != l_type:
                # `int` op `double`
                if l_type == TokenType.INT:
                    l_type = TokenType.DOUBLE
                    self.add_inst(PCode.I2D, at_idx=instruction_idx)
                # `double` op `int`
                elif l_type == TokenType.DOUBLE:
                    self.add_inst(PCode.I2D)

            if l_type == TokenType.DOUBLE:
                self.add_inst(PCode.DCMP)
            else:
                self.add_inst(PCode.ICMP)

            if cmp_op == TokenType.EQ:
                return PCode.JNE
            elif cmp_op == TokenType.NEQ:
                return PCode.JE
            elif cmp_op == TokenType.LESS:
                return PCode.JGE
            elif cmp_op == TokenType.GREATER:
                return PCode.JLE
            elif cmp_op == TokenType.LEQ:
                return PCode.JG
            else:
                assert cmp_op == TokenType.GEQ
                return PCode.JL

    def __analyse_labeled_statement(self, ast: Ast):
        """
        <labeled-statement> ::=
            'case' (<integer-literal>|<char-literal>) ':' <statement>
            |'default' ':' <statement>
        """
        assert_ast_type(ast, AstType.LABELED_STATEMENT)
        print(self)  # to remove the static-warning, nonsense
        raise NotSupportedFeature(get_pos(ast), 'case and default')
        pass

    def __analyse_loop_statement(self, ast: Ast) -> dict:
        """
        <loop-statement> ::=
            'while' '(' <condition> ')' <statement>
            |'do' <statement> 'while' '(' <condition> ')' ';'
            |'for' '('<for-init-statement> [<condition>]';' [<for-update-expression>]')' <statement>
        Return statement statics, e.g. how many `return`s, `while`s
        """
        assert_ast_type(ast, AstType.LOOP_STATEMENT)

        # NOTE: only need to complete `while` loop
        first_token = ast.first_child().token.tok_type
        if first_token == TokenType.WHILE:
            condition = ast.children[2]
            statement = ast.children[4]

            instruction_index_of_condition = self.elf.next_inst_idx()
            jmp_instruction = self.__analyse_condition(condition)
            jmp_instruction_index = self.elf.next_inst_idx()
            self.add_inst(jmp_instruction, 0)

            statements_info = self.__analyse_statement(statement)
            self.add_inst(PCode.JMP, instruction_index_of_condition)
            instruction_index_after_while = self.elf.next_inst_idx()
            offset = instruction_index_after_while
            self.elf.update_instruction_at(jmp_instruction_index, offset)
            return statements_info
        elif first_token == TokenType.DO:
            raise NotSupportedFeature(get_pos(ast), 'do')
        else:
            raise NotSupportedFeature(get_pos(ast), 'for')

    def __analyse_for_init_statement(self, ast: Ast):
        """
        <for-init-statement> ::=
            [<assignment-expression>{','<assignment-expression>}]';'
        """
        assert_ast_type(ast, AstType.FOR_INIT_STATEMENT)

        # NOTE: not base part
        print(self)  # to remove the static-warning, nonsense
        raise NotSupportedFeature(get_pos(ast), 'for-init')

    def __analyse_for_update_expression(self, ast: Ast):
        """
        <for-update-expression> ::=
            (<assignment-expression>|<function-call>){','(<assignment-expression>|<function-call>)}
        """
        assert_ast_type(ast, AstType.FOR_UPDATE_STATEMENT)

        # NOTE: not base part
        print(self)  # to remove the static-warning, nonsense
        raise NotSupportedFeature(get_pos(ast), 'for-update')

    def __analyse_jump_statement(self, ast: Ast) -> dict:
        """
        <jump-statement> ::=
            'break' ';'
            |'continue' ';'
            |<return-statement>
        Return statement statics, e.g. how many `return`s, `while`s
        """
        assert_ast_type(ast, AstType.JUMP_STATEMENT)

        # NOTE: base part only contains <return-statement>
        child_type = ast.first_child().type
        if child_type == Token:
            raise NotSupportedFeature(get_pos(ast), 'break and continue')
        else:
            self.__analyse_return_statement(ast.first_child())
            return {'return': 1}

    def __analyse_return_statement(self, ast: Ast):
        """
        <return-statement> ::= 'return' [<expression>] ';'
        """
        assert_ast_type(ast, AstType.RETURN_STATEMENT)

        return_type = self.elf.current_function().return_type

        if return_type == TokenType.VOID:
            if ast.children[1].type == AstType.EXPRESSION:
                expr_type, _ = self.__analyse_expression(ast.children[1])
                if expr_type != TokenType.VOID:
                    raise ReturnValueForVoidFunction(get_pos(ast.children[1]))
            self.add_inst(PCode.RET)
        else:
            if ast.children[1].type != AstType.EXPRESSION:
                raise NoReturnValueForNotVoidFunction(get_pos(ast))
            expr_type, _ = self.__analyse_expression(ast.children[1])
            self.convert_from_type_to_type(to_type=return_type,
                                           from_type=expr_type,
                                           to_pos=get_pos(ast),
                                           from_pos=get_pos(ast))
            if return_type == TokenType.DOUBLE:
                self.add_inst(PCode.DRET)
            elif return_type == TokenType.INT:
                self.add_inst(PCode.IRET)
            else:
                self.add_inst(PCode.IRET)

    def __analyse_scan_statement(self, ast: Ast):
        """
        <scan-statement> ::=
            'scan' '(' <identifier> ')' ';'
        """
        assert_ast_type(ast, AstType.SCAN_STATEMENT)

        symbol_name = self.__analyse_identifier(ast.children[2])
        constness = self.symbol_table.get_symbol_attr(
            symbol_name, SymbolAttrs.CONSTNESS)

        if constness:
            raise AssignToConstant(get_pos(ast.children[2]))
        else:
            type_ = self.symbol_table.get_type(symbol_name)
            offset = self.symbol_table.get_offset(symbol_name)
            self.add_inst(PCode.LOADA, *offset)

            if type_ == TokenType.INT:
                self.add_inst(PCode.ISCAN)
                self.add_inst(PCode.ISTORE)

            elif type_ == TokenType.DOUBLE:
                self.add_inst(PCode.DSCAN)
                self.add_inst(PCode.DSTORE)

            elif type_ == TokenType.CHAR:
                self.add_inst(PCode.CSCAN)
                self.add_inst(PCode.ISTORE)

            elif type_ == TokenType.VOID:
                raise VoidTypeCalculationNotSupported(get_pos(ast.children[2]))
            else:
                raise UnknownVariableType(get_pos(ast.children[2]), type_)

    def __analyse_assignment_expression(self, ast: Ast):
        """
        <assignment-expression> ::=
            <identifier><assignment-operator><expression>
        """
        assert_ast_type(ast, AstType.ASSIGNMENT_EXPRESSION)

        symbol_name = self.__analyse_identifier(ast.first_child())
        if self.symbol_table.is_const(symbol_name):
            raise AssignToConstant(get_pos(ast.first_child()))

        symbol_type = self.symbol_table.get_type(symbol_name)
        symbol_offset = self.symbol_table.get_offset(symbol_name)
        self.add_inst(PCode.LOADA, *symbol_offset)

        type_, _ = self.__analyse_expression(ast.children[-1])
        self.convert_from_type_to_type(to_type=symbol_type,
                                       from_type=type_,
                                       from_pos=get_pos(ast.children[-1]),
                                       to_pos=get_pos(ast.first_child()))
        if symbol_type == TokenType.DOUBLE:
            self.add_inst(PCode.DSTORE)
        else:
            self.add_inst(PCode.ISTORE)

    def __analyse_print_statement(self, ast: Ast):
        """
        <print-statement> ::=
            'print' '(' [<printable-list>] ')' ';'
        """
        assert_ast_type(ast, AstType.PRINT_STATEMENT)

        if ast.children[2].type == AstType.PRINTABLE_LIST:
            self.__analyse_printable_list(ast.children[2])
        self.add_inst(PCode.PRINTL)

    def __analyse_printable_list(self, ast: Ast):
        """
        <printable-list>  ::=
            <printable> {',' <printable>}
        """
        assert_ast_type(ast, AstType.PRINTABLE_LIST)

        self.__analyse_printable(ast.first_child())
        for child in ast.children[1:]:
            if child.type != AstType.PRINTABLE:
                continue
            self.add_inst(PCode.BIPUSH, 32)
            self.add_inst(PCode.CPRINT)
            self.__analyse_printable(child)

    def __analyse_printable(self, ast: Ast):
        """
        <printable> ::=
            <expression> | <string-literal>
        """
        assert_ast_type(ast, AstType.PRINTABLE)

        child = ast.first_child()
        if child.type == AstType.EXPRESSION:
            type_, _ = self.__analyse_expression(child)
            if type_ == TokenType.VOID:
                raise VoidTypeCalculationNotSupported(get_pos(child))
            elif type_ == TokenType.INT:
                self.add_inst(PCode.IPRINT)
            elif type_ == TokenType.CHAR:
                self.add_inst(PCode.CPRINT)
            else:
                self.add_inst(PCode.DPRINT)
        else:
            self.__analyse_str_literal(child)
            self.add_inst(PCode.SPRINT)

    @staticmethod
    def __analyse_identifier(ast: Ast):
        """
        Return symbol name of the identifier
        """
        assert_ast_type(ast, AstType.IDENTIFIER)
        return ast.first_child().token.value

    @staticmethod
    def __analyse_unary_operator(ast: Ast):
        """
        <unary-operator>          ::= '+' | '-'
        Return type of op, which is one of `TokenType` member
        """
        assert_ast_type(ast, AstType.UNARY_OPERATOR)
        return ast.first_child().token.tok_type

    @staticmethod
    def __analyse_additive_operator(ast: Ast) -> str:
        """
        <additive-operator>       ::= '+' | '-'
        Return type of op, which is one of `TokenType` member
        """
        assert_ast_type(ast, AstType.ADDITIVE_OPERATOR)
        return ast.first_child().token.tok_type

    @staticmethod
    def __analyse_multiplicative_operator(ast: Ast) -> str:
        """
        <multiplicative-operator> ::= '*' | '/'
        Return type of op, which is one of `TokenType` member
        """
        assert_ast_type(ast, AstType.MULTIPLICATIVE_OPERATOR)
        return ast.first_child().token.tok_type

    @staticmethod
    def __analyse_relational_operator(ast: Ast) -> str:
        """
        <relational-operator>     ::= '<' | '<=' | '>' | '>=' | '!=' | '=='
        Return type of op, which is one of `TokenType` member
        """
        assert_ast_type(ast, AstType.RELATIONAL_OPERATOR)
        return ast.first_child().token.tok_type

    @staticmethod
    def __analyse_assignment_operator(ast: Ast) -> str:
        """
        <assignment-operator>     ::= '='
        Return type of op, which is one of `TokenType` member
        """
        assert_ast_type(ast, AstType.ASSIGNMENT_OPERATOR)
        return ast.first_child().token.tok_type

    @staticmethod
    def __analyse_integer_literal(ast: Ast) -> int:
        """
        Return value of the literal
        """
        assert_ast_type(ast, AstType.INTEGER_LITERAL)
        return ast.first_child().token.value

    @staticmethod
    def __analyse_char_literal(ast: Ast) -> str:
        """
        Return value of the literal
        """
        assert_ast_type(ast, AstType.CHAR_LITERAL)
        return ast.first_child().token.value

    @staticmethod
    def __analyse_float_literal(ast: Ast) -> float:
        """
        Return value of the literal
        """
        assert_ast_type(ast, AstType.FLOAT_LITERAL)
        return ast.first_child().token.value

    def __analyse_str_literal(self, ast: Ast):
        """
        Return value of the literal

        Add `str_literal` to constant table, and generate instructions to
        put the address of `str_literal` on stack-top
        """
        assert_ast_type(ast, AstType.STR_LITERAL)

        value = ast.first_child().token.value
        idx = self.elf.add_constant(Constant.STR, value)
        self.add_inst(PCode.LOADC, idx)
