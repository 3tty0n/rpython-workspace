def fn(x):
    if x < 0:
        return x + 1
    else:
        return x - 1

def do_add(x):
    return x + 1

def do_sub(x):
    return x - 1

def we_are_jitted():
    return True

def is_true():
    return True

def interp():
    code = []
    pc = 0
    while 1:
        if code[pc] == "send_fast_path":
            # pc, tstack = t_pop(tstack)
            do_fast_path()
            # go slow path to compile slow path
            # t_stack = t_push(tstack, Bytecode.send_slow_path)
        elif code[pc] == "send_slow_path":
            # t_pop(tstack)
            do_slow_path()
            # go successor
            # pc, tstack = t_pop(tstack)
        elif code[pc] == "send_we_are_jitted":
            if ptr_eq(rcvr, rcvr_type):
                # go send_fast_path
                # tsack = t_push(tstack, Bytecode.send_fast_path)
                pass
