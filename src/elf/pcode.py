class PCode(object):
    SNEW = 'SNEW'

    # IO
    ISCAN = 'ISCAN'
    DSCAN = 'DSCAN'
    CSCAN = 'CSCAN'
    IPRINT = 'IPRINT'
    DPRINT = 'DPRINT'
    CPRINT = 'CPRING'
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

    type_to_size = {

    }

    def __init__(self, inst_type: str, *ops):
        self.operator = inst_type
        self.operands = ops
        self.size = PCode.type_to_size[inst_type]

    def update(self, *args):
        self.operands = args
