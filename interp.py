from rpython.rlib.jit import JitDriver


class W_Object:

    def getrepr(self):
        """
        Return an RPython string which represent the object
        """
        raise NotImplementedError

    def is_true(self):
        raise NotImplementedError

    def add(self, w_other):
        raise NotImplementedError



class W_IntObject(W_Object):

    def __init__(self, intvalue):
        self.intvalue = intvalue

    def getrepr(self):
        return str(self.intvalue)

    def is_true(self):
        return self.intvalue != 0

    def add(self, w_other):
        if isinstance(w_other, W_IntObject):
            sum = self.intvalue + w_other.intvalue
            return W_IntObject(sum)
        else:
            raise OperationError

    def sub(self, w_other):
        if isinstance(w_other, W_IntObject):
            sum = self.intvalue - w_other.intvalue
            return W_IntObject(sum)
        else:
            raise OperationError

class W_StringObject(W_Object):

    def __init__(self, strvalue):
        self.strvalue = strvalue

    def getrepr(self):
        return self.strvalue

    def is_true(self):
        return len(self.strvalue) != 0


class OperationError(Exception):
    pass

# ____________________________________________________________

OPNAMES = []
HASARG = []

def define_op(name, has_arg=False):
    globals()[name] = len(OPNAMES)
    OPNAMES.append(name)
    HASARG.append(has_arg)

define_op("CONST_INT", True)
define_op("POP")
define_op("ADD")
define_op("RETURN")
define_op("JUMP_IF", True)
define_op("DUP")
define_op("SUB")
define_op("NEWSTR", True)


# ____________________________________________________________

def get_printable_location(pc, bytecode):
    op = ord(bytecode[pc])
    name = OPNAMES[op]
    if HASARG[op]:
        arg = str(ord(bytecode[pc + 1]))
    else:
        arg = ''
    return "%s: %s %s" % (pc, name, arg)

jitdriver = JitDriver(
    greens=['pc', 'bytecode'],
    reds=['frame'],
    virtualizables=['frame'],
    get_printable_location=get_printable_location
)

class Frame(object):
    _virtualizable_ = ['stackpos', 'stack[*]']

    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.stack = [None] * 8
        self.stackpos = 0

    def push(self, w_x):
        self.stack[self.stackpos] = w_x
        self.stackpos += 1

    def pop(self):
        stackpos = self.stackpos - 1
        assert stackpos >= 0
        self.stackpos = stackpos
        res = self.stack[stackpos]
        self.stack[stackpos] = None
        return res


def _CONST_INT(frame, pc):
    value = ord(frame.bytecode[pc])
    w_z = W_IntObject((value))
    frame.push(w_z)


def _POP(frame):
    frame.pop()


def _DUP(frame):
    w_x = frame.pop()
    frame.push(w_x)
    frame.push(w_x)


def _ADD(frame):
    w_y = frame.pop()
    w_x = frame.pop()
    w_z = w_x.add(w_y)
    frame.push(w_z)


def _SUB(frame):
    w_y = frame.pop()
    w_x = frame.pop()
    w_z = w_x.sub(w_y)
    frame.push(w_z)


def _NEWSTR(frame, pc):
    char = frame.bytecode[pc]
    # pc += 1
    w_z = W_StringObject(char)
    frame.push(w_z)


def _RETURN(frame):
    return frame.pop()


def interp(frame, pc=0):

    bytecode = frame.bytecode

    while pc < len(bytecode):
        jitdriver.jit_merge_point(
            frame=frame,
            bytecode=bytecode,
            pc=pc,
        )
        opcode = ord(bytecode[pc])
        pc += 1

        if opcode == CONST_INT:
            _CONST_INT(frame, pc)
            pc += 1

        elif opcode == POP:
            _POP(frame)

        elif opcode == DUP:
            _DUP(frame)

        elif opcode == ADD:
            _ADD(frame)

        elif opcode == SUB:
            _SUB(frame)

        elif opcode == JUMP_IF:
            target = ord(bytecode[pc])
            pc += 1
            w_x = frame.pop()
            if w_x.is_true():
                pc = target
                jitdriver.can_enter_jit(
                    frame=frame,
                    bytecode=bytecode,
                    pc=pc
                )

        elif opcode == NEWSTR:
            _NEWSTR(frame, pc)
            pc += 1

        elif opcode == RETURN:
            return _RETURN(frame)

        else:
            assert False, 'Unknown opcode: %d' % opcode

def run(bytecode, w_arg):
    frame = Frame(bytecode)
    frame.push(w_arg)
    w_result = interp(frame)
    return w_result
