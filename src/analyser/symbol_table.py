from typing import Dict


class SymbolTable(object):
    def __init__(self):
        self.level_tables = []

    def add_symbol(self, symbol):
        pass

    def update_symbol(self, symbol):
        pass

    def get_symbol_info(self, symbol_name):
        pass

    def enter_level(self):
        self.level_tables.append(LevelSymbolTable())

    def exit_level(self):
        self.level_tables.pop()


class LevelSymbolTable(object):
    def __init__(self):
        self.symbols: Dict[str, dict] = {}

    def add_symbol(self, symbol: str):
        self.symbols[symbol] = {}

    def update_symbol(self, symbol: str, key: str, value):
        self.symbols[symbol][key] = value

    def get_symbol_info(self, symbol_name, key: str):
        return self.symbols[symbol_name][key]
