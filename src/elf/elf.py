from elf.pcode import PCode
from typing import List, Union


class Constant(object):
    STR = 'S'
    INT = 'I'
    DOUBLE = 'D'

    def __init__(self, type_: str, value):
        self.type_ = type_
        self.value = value


class Function(object):
    def __init__(self, name: str, return_type: str, instructions: List[PCode]):
        self.name = name
        self.return_type = return_type
        self.instructions = instructions
        self.param_count: int = ...


class ELF(object):
    def __init__(self):
        # global instructions
        self.instructions: List[PCode] = []
        self.constants: List[Constant] = []
        self.functions: List[Function] = []
        self.start = ...

    def add_constant(self, type_: str, value):
        """
        Add consant to elf and return corresponding index
        If constant already existed, this method won't make a new copy
        """
        assert type_ in [Constant.STR, Constant.INT,
                         Constant.DOUBLE], 'Error constant type'
        for idx, const in enumerate(self.constants):
            if (const.type_, const.value) == (type_, value):
                return idx
        self.constants.append(Constant(type_, value))
        return len(self.constants) - 1

    def current_function(self) -> Union[Function, None]:
        return self.functions[-1] if self.functions else None

    def next_inst_idx(self) -> int:
        if self.functions:
            return len(self.functions[-1].instructions)
        return len(self.instructions)

    def instruction_offset_from_to(self, frm: int, to: int) -> int:
        """
        :return offset from `frm` to `to`, addr_frm + return_value = addr_to
        """
        if frm > to:
            return -self.instruction_offset_from_to(to, frm)
        offset = 0
        while frm < to:
            offset += self.instructions[frm].size
            frm += 1
        return offset

    def add_function(self, return_type: str, func_name: str):
        assert not self.has_function(
            func_name), 'Please check function not contained first'
        self.functions.append(
            Function(name=func_name, return_type=return_type, instructions=[]))

    def has_function(self, func_name: str) -> bool:
        for func in self.functions:
            if func.name == func_name:
                return True
        return False

    def function_index(self, func_name: str) -> int:
        assert self.has_function(
            func_name), 'Please check function contained first'
        for idx, func in enumerate(self.functions):
            if func.name == func_name:
                return idx

    def function_param_count(self, func_name: str) -> int:
        assert self.has_function(
            func_name), 'Please check function contained first'
        for func in self.functions:
            if func.name == func_name:
                return func.param_count

    def function_return_type(self, func_name: str) -> str:
        assert self.has_function(
            func_name), 'Please check function contained first'
        for function in self.functions:
            if function.name == func_name:
                return function.return_type

    def current_instructions(self):
        if not self.functions:
            return self.functions[-1].instructions
        return self.instructions

    def update_instruction_at(self, idx: int, *args):
        self.current_instructions()[idx].update(*args)

    def generate_s0(self):
        """
        Generate output ELF file, output is like:

        .constants:
            {index} {type} {value}
            ...
        .start:
            {index} {opcode} {operands}
            ...
        .functions:
            {index} {name_index} {params_size} {level}
            ...
        .F0:
            {index} {opcode} {operands}
            ...
        .F1:
            {index} {opcode} {operands}
            ...
        ...
        .F{functions_count-1}:
            {index} {opcode} {operands}
            ...
        """
        '''
        find a function-definition -> add name to const-list
        '''
        pass
