from typing import Dict, List, Tuple


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
            'sizes': (1, 4),
            'operands': 1,
            'code': 0x0c
        },

        ISCAN: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xb0
        },
        DSCAN: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xb1
        },
        CSCAN: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xb2
        },
        IPRINT: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xa0
        },
        DPRINT: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xa1
        },
        CPRINT: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xa2
        },
        SPRINT: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xa3
        },
        PRINTL: {
            'sizes': (1,),
            'operands': 0,
            'code': 0xaf
        },

        CALL: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x80
        },
        RET: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x88
        },
        IRET: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x89
        },
        DRET: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x8a
        },
        JE: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x71
        },
        JNE: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x72
        },
        JL: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x73
        },
        JLE: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x76
        },
        JG: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x75
        },
        JGE: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x74
        },
        JMP: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x70
        },

        LOADA: {
            'sizes': (1, 2, 4),
            'operands': 2,
            'code': 0x0a
        },
        ILOAD: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x10
        },
        DLOAD: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x11
        },
        LOADC: {
            'sizes': (1, 2),
            'operands': 1,
            'code': 0x09
        },
        ISTORE: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x20
        },
        DSTORE: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x21
        },

        I2D: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x60
        },
        D2I: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x61
        },
        I2C: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x62
        },

        DADD: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x31
        },
        IADD: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x30
        },
        DSUB: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x35
        },
        ISUB: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x34
        },
        DMUL: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x39
        },
        IMUL: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x38
        },
        DDIV: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x3d
        },
        IDIV: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x3c
        },
        DNEG: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x41
        },
        INEG: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x40
        },

        BIPUSH: {
            'sizes': (1, 1),
            'operands': 1,
            'code': 0x01
        },
        IPUSH: {
            'sizes': (1, 4),
            'operands': 1,
            'code': 0x02
        },

        ICMP: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x44
        },
        DCMP: {
            'sizes': (1,),
            'operands': 0,
            'code': 0x45
        },
    }

    def __init__(self, inst_type: str, *ops):
        # print(f'create {inst_type} with {ops}')
        self.operator = inst_type
        self.operands: Tuple[int] = ops
        self.size = PCode.type_to_info[inst_type]['sizes']
        self.__check_syntax()

    def update(self, *args):
        # print(f'Update from `{self}` to ', end='')
        self.operands = args
        # print(f'`{self}`\n')
        self.__check_syntax()

    def __check_syntax(self):
        info = PCode.type_to_info[self.operator]
        operands = info['operands']
        sizes = info['sizes']
        if len(sizes) - 1 != operands:
            raise Exception('Fatal error, configuration illegal')

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
