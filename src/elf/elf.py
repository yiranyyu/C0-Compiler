from elf.pcode import PCode
from typing import List, Union, Dict
from analyser.symbol_table import type_to_size
import struct


def print_hex_byte(byte_seq: bytes):
    print(' '.join(str(hex(x))[2:].zfill(2) for x in byte_seq))


class Constant(object):
    STR = 'S'
    INT = 'I'
    DOUBLE = 'D'

    str_to_binary: Dict[str, int] = {
        STR: 0,
        INT: 1,
        DOUBLE: 2
    }

    def __init__(self, type_: str, value):
        self.type_ = type_
        self.value = value
        self.binary_type = Constant.str_to_binary[self.type_]


class Function(object):
    def __init__(self, name: str, return_type: str, name_idx: int, params_info: List[str], instructions: List[PCode]):
        self.name = name
        self.name_idx = name_idx
        self.return_type = return_type
        self.instructions = instructions
        self.param_info: List[str] = params_info
        self.param_size = self.__init_param_size()

    def __init_param_size(self):
        size = 0
        for param_type in self.param_info:
            size += type_to_size[param_type]
        return size


class ELF(object):
    def __init__(self):
        # global instructions
        self.instructions: List[PCode] = []
        self.constants: List[Constant] = []
        self.functions: List[Function] = []
        self.start = ...

    def add_constant(self, type_: str, value):
        """
        Add constant to elf and return corresponding index
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

    def add_function(self, return_type: str, func_name: str, name_idx: int, params_info: List[str]):
        assert not self.has_function(
            func_name), 'Please check function not contained first'
        self.functions.append(
            Function(name=func_name, return_type=return_type, name_idx=name_idx, params_info=params_info,
                     instructions=[]))

    def has_function(self, func_name: str) -> bool:
        for func in self.functions:
            if func.name == func_name:
                return True
        return False

    def function_params_info(self, func_name: str) -> List[str]:
        assert self.has_function(
            func_name), 'Please check function contained first'
        for idx, func in enumerate(self.functions):
            if func.name == func_name:
                return func.param_info

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
                return len(func.param_info)

    def function_return_type(self, func_name: str) -> str:
        assert self.has_function(
            func_name), 'Please check function contained first'
        for function in self.functions:
            if function.name == func_name:
                return function.return_type

    def current_instructions(self):
        if self.functions:
            return self.functions[-1].instructions
        return self.instructions

    def update_instruction_at(self, idx: int, *args):
        self.current_instructions()[idx].update(*args)

    def generate_o0(self) -> bytes:
        """
        // i2,i3,i4的内容，以大端序（big-endian）写入文件
        typedef int8_t  i1;
        typedef int16_t i2;
        typedef int32_t i4;
        typedef int64_t i8;

        // u2,u3,u4的内容，以大端序（big-endian）写入文件
        typedef uint8_t  u1;
        typedef uint16_t u2;
        typedef uint32_t u4;
        typedef uint64_t u8;

        struct String_info {
            u2 length;
            u1 value[length];
        };

        struct Int_info {
            i4 value;
        };

        struct Double_info {
            u4 high_bytes;
            u4 low_bytes;
        };

        struct Constant_info {
            // STRING = 0,
            // INT = 1,
            // DOUBLE = 2
            u1 type;
            // 根据type决定是String_info 还是 Int_info 还是 Double_info
            u1 info[];
        };

        struct Instruction {
            u1 opcode;
            u1 operands[/* size depends on opcode */];
        };

        struct Function_info {
            u2          name_index; // name: CO_binary_file.strings[name_index]
            u2          params_size;
            u2          level;
            u2          instructions_count;
            Instruction instructions[instructions_count];
        };

        struct Start_code_info {
            u2          instructions_count;
            Instruction instructions[instructions_count];
        }

        struct C0_binary_file {
            u4              magic; // must be 0x43303A29
            u4              version;
            u2              constants_count;
            Constant_info   constants[constants_count];
            Start_code_info start_code;
            u2              functions_count;
            Function_info   functions[functions_count];
        };
        """
        byteorder = 'big'

        def twos_comp(val: int, bits: int) -> int:
            if val >= 0:
                return val
            return val + (1 << bits)

        def double_binary(x: float):
            return struct.pack('>d', x)

        output = bytes()

        magic = (0x43303A29).to_bytes(4, byteorder)
        output += magic

        version = (0x01).to_bytes(4, byteorder)
        output += version

        constants_count = len(self.constants).to_bytes(2, byteorder)
        output += constants_count

        # Constant_info
        for const in self.constants:
            binary_type = const.binary_type.to_bytes(1, byteorder)
            info = bytes()

            if const.type_ == Constant.STR:
                info += len(const.value).to_bytes(2, byteorder)
                info += bytes(const.value, encoding='ASCII')
            elif const.type_ == Constant.INT:
                info += twos_comp(const.value, 32).to_bytes(4, byteorder)
            elif const.type_ == Constant.DOUBLE:
                info += double_binary(const.value)
            else:
                raise Exception('Fatal error, unrecognized constant type')
            output += binary_type + info

        # Start_code_info
        instruction_count = len(self.instructions).to_bytes(2, byteorder)
        output += instruction_count

        for instruction in self.instructions:
            instruction_info = PCode.type_to_info[instruction.operator]
            operator = instruction_info['code'].to_bytes(1, byteorder)
            operands = []
            for size, operand in zip(instruction_info['sizes'][1:], instruction.operands):
                operands.append(operand.to_bytes(size, byteorder))

            output += operator + b''.join(operands)
            # print(instruction)
            # print_hex_byte(operator + b''.join(operands))

        functions_count = len(self.functions).to_bytes(2, byteorder)
        output += functions_count

        # Function_info
        for function in self.functions:
            name_index = function.name_idx.to_bytes(2, byteorder)
            output += name_index

            params_size = function.param_size.to_bytes(2, byteorder)
            output += params_size

            level = (1).to_bytes(2, byteorder)
            output += level

            instruction_count = len(function.instructions).to_bytes(2, byteorder)
            output += instruction_count

            for instruction in function.instructions:
                instruction_info = PCode.type_to_info[instruction.operator]
                operator = instruction_info['code'].to_bytes(1, byteorder)
                operands = []
                for size, operand in zip(instruction_info['sizes'][1:], instruction.operands):
                    operands.append(operand.to_bytes(size, byteorder))

                output += operator + b''.join(operands)
                # print(instruction)
                # print_hex_byte(operator + b''.join(operands))

        return output

    def generate_s0(self) -> str:
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
        output = ''

        # constants
        output += '.constants:\n'
        for idx, const in enumerate(self.constants):
            value = const.value
            if const.type_ == Constant.STR:
                value = f'"{repr(value)[1:-1]}"'
            output += f'    {idx: 5} {const.type_} {value}\n'

        # start
        output += '.start:\n'
        for idx, instruction in enumerate(self.instructions):
            output += f'    {idx: 5} {instruction}\n'

        # functions
        output += '.functions:\n'
        for idx, function in enumerate(self.functions):
            output += f'    {idx: >3} {function.name_idx: >3} {function.param_size: >3} {1: >3}\n'

        # function definitions
        for func in self.functions:
            output += f'{func.name}:\n'
            for idx, instruction in enumerate(func.instructions):
                output += f'    {idx: >3} {instruction}\n'

        return output
