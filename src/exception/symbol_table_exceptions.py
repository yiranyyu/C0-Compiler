class SymbolTableException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class SymbolWithoutType(SymbolTableException):
    def __init__(self, symbol_name: str):
        super().__init__(
            f'Try to insert `{symbol_name}` into symbol table without type info')


class SymbolNotFound(SymbolTableException):
    def __init__(self, symbol_name: str):
        super().__init__(f'Symbol `{symbol_name}` not found.')


class FunctionTypeHasNoOffsetAttribute(SymbolTableException):
    def __init__(self, symbol_name: str):
        super().__init__(f'Symbol `{symbol_name}` is a function, but received a request for offset')
