from interp import DUP, CONST_INT, SUB, DUP, JUMP_IF, POP, RETURN

code = [
    DUP,
    CONST_INT, 1,
    SUB,
    DUP,
    JUMP_IF, 1,
    POP,
    CONST_INT, 1,
    SUB,
    DUP,
    JUMP_IF, 0,
    RETURN
    ]
