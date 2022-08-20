from bin_types.function import Function
from bin_types.list import List
from parsing.oper import OpIds, Oper
from .tc_types import TypeCheckedFunction

def tc_line1(op : Oper, state):
    """Executes 1 stage of type checking for 1 keyword"""
    is_func = bool(state.opened_function)
    local = state.opened_function.locals if is_func else {}
    full_vars = {**state.vars, **local}

    state.current_line = op.line

    if op.id == OpIds.value:
        return type(op.values[0])

    elif op.id == OpIds.variable:
        if op.values[0] not in full_vars:
            state.warnings += 1
            return object

        return full_vars[op.values[0]]

    elif op.id == OpIds.operation:
        if op.values[0] in state.int_operations:
            return int
        elif op.values[0] in state.float_operations:
            return float
        elif issubclass(tc_line1(op.args[0], state), float) or\
        issubclass(tc_line1(op.args[1], state), float):
            return float
        elif issubclass(tc_line1(op.args[0], state), str) or\
        issubclass(tc_line1(op.args[1], state), str) and\
        op.values[0] in state.iter_operations:
            return str
        elif issubclass(tc_line1(op.args[0], state), List) or\
        issubclass(tc_line1(op.args[1], state), List) and\
        op.values[0] in state.iter_operations:
            return List
        else:
            return int

    elif op.id == OpIds.var:
        if is_func:
            if op.types:
                local[op.values[0]] = op.types[0]
            elif local.get(op.values[0], None) in (None, object):
                local[op.values[0]] = tc_line1(op.args[0], state)
        else:
            if op.types:
                state.vars[op.values[0]] = op.types[0]
            elif state.vars.get(op.values[0], None) in (None, object):
                state.vars[op.values[0]] = tc_line1(op.args[0], state)

    elif op.id == OpIds.convert:
        return op.values[0]

    elif op.id == OpIds.if_ or op.id == OpIds.else_ or op.id == OpIds.elif_ or op.id == OpIds.while_:
        for i in op.oper:
            tc_line1(i, state)

    elif op.id == OpIds.for_:
        if is_func:
            local[op.args[0]] = object
        else:
            state.vars[op.args[0]] = object

        for i in op.oper:
            tc_line1(i, state)

    elif op.id == OpIds.func:
        func = TypeCheckedFunction(op.oper, list(zip(op.values[1:], op.types[1:])), op.types[0])
        state.functions[op.values[0]] = func
        full_vars[op.values[0]] = Function
        state.opened_function = func
        for i in op.oper:
            tc_line1(i, state)
        state.opened_function = None

    elif op.id == OpIds.call:
        called = op.args[0].values[0]
        if called not in state.functions:
            state.warnings += 1
            return object
        return state.functions[called].ret

    else:
        if op.id.name in state.keywords:
            keyword = state.keywords[op.id.name]

            return keyword[0]

        state.warnings += 1