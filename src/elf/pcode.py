from typing import Dict


class PCode(object):
    SNEW = 'SNEW'

    # IO
    ISCAN = 'ISCAN'
    DSCAN = 'DSCAN'
    CSCAN = 'CSCAN'
    IPRINT = 'IPRINT'
    DPRINT = 'DPRINT'
    CPRINT = 'CPRINT'
    SPRINT = 'SPRINT'
    PRINTL = 'PRINTL'

    # control-stream
    CALL = 'CALL'
    RET = 'RET'
    IRET = 'IRET'
    DRET = 'DRET'
    JE = 'JE'
    JNE = 'JNE'
    JL = 'JL'
    JLE = 'JLE'
    JG = 'JG'
    JGE = 'JGE'
    JMP = 'JMP'

    # load
    LOADA = 'LOADA'
    ILOAD = 'ILOAD'
    DLOAD = 'DLOAD'
    LOADC = 'LOADC'

    # store
    ISTORE = 'ISTORE'
    DSTORE = 'DSTORE'

    # casting
    I2D = 'I2D'
    D2I = 'D2I'
    I2C = 'I2C'

    # calculating
    DADD = 'DADD'
    IADD = 'IADD'
    DSUB = 'DSUB'
    ISUB = 'ISUB'
    DMUL = 'DMUL'
    IMUL = 'IMUL'
    DDIV = 'DDIV'
    IDIV = 'IDIV'
    DNEG = 'DNEG'
    INEG = 'INEG'

    # stack-manipulation
    BIPUSH = 'BIPUSH'
    IPUSH = 'IPUSH'

    # compare
    ICMP = 'ICMP'
    DCMP = 'DCMP'

    type_to_info: Dict[str, dict] = {
        SNEW: {
            'size': 1 + 4,
            'operands': 1,
            'code': 0x0c
        },

        ISCAN: {
            'size': 1,
            'operands': 0,
            'code': 0xb0
        },
        DSCAN: {
            'size': 1,
            'operands': 0,
            'code': 0xb1
        },
        CSCAN: {
            'size': 1,
            'operands': 0,
            'code': 0xb2
        },
        IPRINT: {
            'size': 1,
            'operands': 0,
            'code': 0xa0
        },
        DPRINT: {
            'size': 1,
            'operands': 0,
            'code': 0xa1
        },
        CPRINT: {
            'size': 1,
            'operands': 0,
            'code': 0xa2
        },
        SPRINT: {
            'size': 1,
            'operands': 0,
            'code': 0xa3
        },
        PRINTL: {
            'size': 1,
            'operands': 0,
            'code': 0xaf
        },

        CALL: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x80
        },
        RET: {
            'size': 1,
            'operands': 0,
            'code': 0x88
        },
        IRET: {
            'size': 1,
            'operands': 0,
            'code': 0x89
        },
        DRET: {
            'size': 1,
            'operands': 0,
            'code': 0x8a
        },
        JE: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x71
        },
        JNE: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x72
        },
        JL: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x73
        },
        JLE: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x76
        },
        JG: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x75
        },
        JGE: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x74
        },
        JMP: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x70
        },

        LOADA: {
            'size': 1 + 2 + 4,
            'operands': 2,
            'code': 0x0a
        },
        ILOAD: {
            'size': 1,
            'operands': 0,
            'code': 0x10
        },
        DLOAD: {
            'size': 1,
            'operands': 0,
            'code': 0x11
        },
        LOADC: {
            'size': 1 + 2,
            'operands': 1,
            'code': 0x09
        },
        ISTORE: {
            'size': 1,
            'operands': 0,
            'code': 0x20
        },
        DSTORE: {
            'size': 1,
            'operands': 0,
            'code': 0x21
        },

        I2D: {
            'size': 1,
            'operands': 0,
            'code': 0x60
        },
        D2I: {
            'size': 1,
            'operands': 0,
            'code': 0x61
        },
        I2C: {
            'size': 1,
            'operands': 0,
            'code': 0x62
        },

        DADD: {
            'size': 1,
            'operands': 0,
            'code': 0x31
        },
        IADD: {
            'size': 1,
            'operands': 0,
            'code': 0x30
        },
        DSUB: {
            'size': 1,
            'operands': 0,
            'code': 0x35
        },
        ISUB: {
            'size': 1,
            'operands': 0,
            'code': 0x34
        },
        DMUL: {
            'size': 1,
            'operands': 0,
            'code': 0x39
        },
        IMUL: {
            'size': 1,
            'operands': 0,
            'code': 0x38
        },
        DDIV: {
            'size': 1,
            'operands': 0,
            'code': 0x3d
        },
        IDIV: {
            'size': 1,
            'operands': 0,
            'code': 0x3c
        },
        DNEG: {
            'size': 1,
            'operands': 0,
            'code': 0x41
        },
        INEG: {
            'size': 1,
            'operands': 0,
            'code': 0x40
        },

        BIPUSH: {
            'size': 1 + 1,
            'operands': 1,
            'code': 0x01
        },
        IPUSH: {
            'size': 1 + 4,
            'operands': 1,
            'code': 0x02
        },

        ICMP: {
            'size': 1,
            'operands': 0,
            'code': 0x44
        },
        DCMP: {
            'size': 1,
            'operands': 0,
            'code': 0x45
        },
    }

    def __init__(self, inst_type: str, *ops):
        # print(f'create {inst_type} with {ops}')
        self.operator = inst_type
        self.operands = ops
        self.size = PCode.type_to_info[inst_type]['size']
        self.__check_syntax()

    def update(self, *args):
        # print(f'Update from `{self}` to ', end='')
        self.operands = args
        # print(f'`{self}`\n')
        self.__check_syntax()

    def __check_syntax(self):
        info = PCode.type_to_info[self.operator]
        operands = info['operands']

        error_msg = f'{operands} operands need of {self.operator}, but got {len(self.operands)}'
        assert (len(self.operands) == operands), error_msg

    def __str__(self):
        output = ''
        output += self.operator
        for idx, x in enumerate(self.operands):
            if idx:
                output += ','
            output += f' {x}'
        return output
