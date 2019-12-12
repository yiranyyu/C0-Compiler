from typing import Dict, List, Tuple
from exception.symbol_table_exceptions import *
from tokenizer import TokenType


class SymbolAttrs(object):
    VALUE = 'VALUE'
    CONSTNESS = 'CONSTNESS'
    OFFSET = 'OFFSET'
    SIZE = 'SIZE'
    IS_FUNC = 'IS_FUNC'

    # corresponding value must be one of `TokenType.types`
    TYPE = 'TYPE'

    # works if symbol type is in [function] , then its value can be found in the
    # corresponding entry of the constant-table
    VALUE_IDX = 'VALUE_IDX'


# size measured by `slot`s, 1 slot is 4 byte
type_to_size = {
    TokenType.INT: 1,
    TokenType.DOUBLE: 2,
    TokenType.CHAR: 2,
}


def get_type_size(attrs: dict) -> int:
    type_ = attrs[SymbolAttrs.TYPE]
    return type_to_size[type_]


class LevelSymbolTable(object):
    def __init__(self):
        self.symbols: Dict[str, dict] = {}
        self.next_offset = 0

    def add_symbol(self, symbol_name: str, attrs: dict):
        """
        This function will modify the offset automatically
        :param symbol_name: name of symbol to be inserted
        :param attrs: attributes of symbol, keys must be member of `SymbolAttr`
        """
        if SymbolAttrs.TYPE not in attrs:
            raise SymbolWithoutType(symbol_name)

        attrs[SymbolAttrs.SIZE] = get_type_size(attrs)
        attrs[SymbolAttrs.OFFSET] = self.next_offset
        if SymbolAttrs.IS_FUNC not in attrs:
            attrs[SymbolAttrs.IS_FUNC] = False

        self.next_offset += attrs[SymbolAttrs.SIZE]
        self.symbols[symbol_name] = attrs

    def update_symbol(self, symbol_name: str, key: str, value):
        self.symbols[symbol_name][key] = value

    def get_symbol_attr(self, symbol_name: str, key: str):
        return self.symbols[symbol_name][key]

    def get_symbol_info(self, symbol_name: str) -> dict:
        return self.symbols[symbol_name]

    def initialized(self, symbol_name: str) -> bool:
        return SymbolAttrs.TYPE in self.symbols[symbol_name]

    def __contains__(self, symbol_name: str) -> bool:
        return symbol_name in self.symbols


class SymbolTable(object):
    def __init__(self):
        # [cur_level, prev_level, ..., global_level]
        self.level_tables: List[LevelSymbolTable] = []

    def __assert_contains(self, symbol_name: str):
        if symbol_name not in self.level_tables:
            raise SymbolNotFound(symbol_name)

    def add_symbol(self, symbol_name: str, attrs: dict = None):
        """
        This function will modify the offset automatically
        :param symbol_name: name of symbol to be inserted
        :param attrs: attributes of symbol, keys must be member of `SymbolAttr`
        """
        if attrs is None:
            attrs = {}
        self.current_level().add_symbol(symbol_name, attrs)

    def update_symbol(self, symbol_name: str, key: str, value):
        self.__assert_contains(symbol_name)
        for table in self.level_tables:
            if symbol_name in table:
                return table.update_symbol(symbol_name, key, value)

    def get_symbol_attr(self, symbol_name: str, key: str):
        self.__assert_contains(symbol_name)
        for table in self.level_tables:
            if symbol_name in table:
                return table.get_symbol_attr(symbol_name, key)

    def is_function(self, symbol_name: str):
        self.__assert_contains(symbol_name)
        table = self.level_tables[-1]
        if symbol_name in table:
            return table.get_symbol_attr(symbol_name, SymbolAttrs.IS_FUNC)
        raise

    def is_const(self, symbol_name: str) -> bool:
        self.__assert_contains(symbol_name)
        for idx, table in enumerate(self.level_tables):
            if symbol_name in table:
                return table.get_symbol_attr(symbol_name, SymbolAttrs.CONSTNESS)

    def get_offset(self, symbol_name: str) -> Tuple[int, int]:
        """
        :return tuple of (level_difference, stack_offset)
        """
        self.__assert_contains(symbol_name)
        for idx, table in enumerate(self.level_tables):
            if symbol_name in table:
                return idx, table.get_symbol_attr(symbol_name, SymbolAttrs.OFFSET)

    def get_size(self, symbol_name: str):
        self.__assert_contains(symbol_name)
        for table in self.level_tables:
            if symbol_name in table:
                return table.get_symbol_attr(symbol_name, SymbolAttrs.SIZE)

    def get_type(self, symbol_name: str):
        self.__assert_contains(symbol_name)
        for table in self.level_tables:
            if symbol_name in table:
                return table.get_symbol_attr(symbol_name, SymbolAttrs.TYPE)

    def get_symbol_info(self, symbol_name: str) -> dict:
        self.__assert_contains(symbol_name)
        for table in self.level_tables:
            if symbol_name in table:
                return table.get_symbol_info(symbol_name)

    def current_level(self) -> LevelSymbolTable:
        return self.level_tables[-1]

    def enter_level(self):
        self.level_tables.insert(0, LevelSymbolTable())

    def exit_level(self):
        self.level_tables.pop(0)

    def __contains__(self, symbol_name: str) -> bool:
        for table in self.level_tables[::-1]:
            if symbol_name in table:
                return True
        return False
