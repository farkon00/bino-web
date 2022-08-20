from .oper import *
from .get_args import *
from funcs.exceptions import *
from funcs.utils import is_name_unavailable
from type_checking.get_type import get_type

def parse_to_ops(state):
    opers = []
    for line_index in range(len(state.lines)):
        # For skiping, that was already parsed inside blocks 
        if state.current_line > line_index:
            continue

        state.current_line += 1
        if state.current_line >= len(state.lines):
            break
        line = state.lines[state.current_line]

        op = parse_line(line, state)
        if op:
            opers.append(op)

    state.current_line = -1
    return opers

def parse_block(state, start):
    opers = []
    binarian_assert(not state.lines[start].strip().endswith("{"), 'Block not found', state)
    for line_index in range(start, len(state.lines)):
        # For skiping, that was already parsed inside other blocks
        if state.current_line > line_index:
            continue

        state.current_line += 1
        if state.current_line >= len(state.lines):
            break

        line = state.lines[state.current_line]

        op = parse_line(line, state)
        if op:
            opers.append(op)

        if "}" in line:
            return opers

    throw_exception('Block must have start and finish matched with ""{" and "}"', state, False)

def parse_line(line, state):
    lexic = line.split()

    if len(lexic) <= 0:
        return

    lexic[0] = lexic[0].replace("}", "").replace("{", "")

    if lexic[0].strip() == "":
        del lexic[0]

    if len(lexic) <= 0:
        return

    if lexic[0] in state.operations:
        op = Oper(OpIds.operation, state.current_line, get_args(lexic[1:], state), values=[lexic[0]]) 
        binarian_assert(len(op.args) != 2, "Operation must have two argument.", state)
        return op

    if lexic[0] == "var":
        parts = [None, None]
        for j, i in enumerate(lexic):
            if "=" in i:
                spl = i.find("=")
                parts[0] = lexic[:j] + [i[:spl]]
                parts[1] = [i[spl + 1:]] + lexic[j + 1:]
                break

        if not parts[0][-1]: parts[0] = parts[0][:-1]
        if not parts[1][0]: parts[1] = parts[1][1:]
        binarian_assert(len(parts[0]) < 2, "Variable must have name and value.", state)
        
        if len(parts[0]) == 3:
            type_ = get_type(parts[0][1], state, {}, True)
            name = parts[0][2].strip()
        else:
            type_ = None
            name = parts[0][1].strip()

        binarian_assert(is_name_unavailable(name, state), f"Variable name is unavailiable : {name}", state)

        op = Oper(OpIds.var, state.current_line, get_args(parts[1], state), values=[name], types=type_)
        binarian_assert(len(op.args) != 1, "Variable must have only one value.", state)
        return op

    elif lexic[0] == "drop":
        binarian_assert(len(lexic) != 2, "Drop must have one argument.", state)
        binarian_assert(is_name_unavailable(lexic[1], state), f"Variable name is unavailiable : {lexic[0]}", state)
        return Oper(OpIds.drop, state.current_line, values=[lexic[1]])

    elif lexic[0] == "input":
        binarian_assert(len(lexic) != 1, "Input must have no argument.", state)
        return Oper(OpIds.input, state.current_line)

    elif lexic[0] == "convert":
        binarian_assert(lexic[-1] not in state.types, f"Type was not found : {lexic[-1]}", state)
        op = Oper(OpIds.convert, state.current_line, get_args(lexic[1:-1], state), values=[get_type(lexic[-1], state, {}, True)])
        binarian_assert(len(op.args) != 1, "Convert must have two argument.", state)
        return op

    elif lexic[0] == "and" or lexic[0] == "or":
        op = Oper(type.__getattribute__(OpIds, lexic[0] + "_"), state.current_line, get_args(lexic[1:], state))
        binarian_assert(len(op.args) != 2, f"{lexic[0][0].upper() + lexic[0][1:]} must have two argument.", state)
        return op

    elif lexic[0] == "not":
        op = Oper(OpIds.not_, state.current_line, get_args(lexic[1:], state))
        binarian_assert(len(op.args) != 1, "Not must have one argument.", state)
        return op

    elif lexic[0] == "index" or lexic[0] == "append" or lexic[0] == "zip":
        op = Oper(type.__getattribute__(OpIds, lexic[0]), state.current_line, get_args(lexic[1:], state))
        binarian_assert(len(op.args) != 2, f"{lexic[0][0].upper() + lexic[0][1:]} must have two argument.", state)
        return op

    elif lexic[0] == "setindex" or lexic[0] == "pyeval":
        op = Oper(type.__getattribute__(OpIds, lexic[0]), state.current_line, get_args(lexic[1:], state))
        binarian_assert(len(op.args) != 3, f"{lexic[0][0].upper() + lexic[0][1:]} must have three argument.", state)
        return op

    elif lexic[0] == "if" or lexic[0] == "elif" or lexic[0] == "while":
        op = Oper(type.__getattribute__(OpIds, lexic[0] + "_"), state.current_line, get_args(lexic[1:], state))
        binarian_assert(len(op.args) != 1, f"{lexic[0][0].upper() + lexic[0][1:]} must have one argument.", state)
        op.oper = parse_block(state, state.current_line)
        return op
    
    elif lexic[0] == "else":
        op = Oper(OpIds.else_, state.current_line, get_args(lexic[1:], state))
        binarian_assert(len(op.args) != 0, "Else must have no argument.", state)
        op.oper = parse_block(state, state.current_line)
        return op

    elif lexic[0] == "for":
        op = Oper(OpIds.for_, state.current_line, get_args(lexic[2:], state), values=[lexic[1]])
        binarian_assert(len(op.args) != 1, "For must have two argument.", state)
        binarian_assert(is_name_unavailable(op.values[0], state), f"For variable name is unavailable : {op.args[0]}", state)
        op.oper = parse_block(state, state.current_line)
        return op

    elif lexic[0] == "break" or lexic[0] == "continue":
        binarian_assert(len(lexic) != 1, f"{lexic[0][0].upper() + lexic[0][1:]} must have no arguments.", state)
        return Oper(type.__getattribute__(OpIds, lexic[0] + "_"), state.current_line,)

    elif lexic[0] == "func":
        parts = line.split(":", maxsplit=1)
        parts[0] = parts[0].replace("{", "").replace("}", "").split()

        binarian_assert(len(parts[0]) < 2, "Function must have name.", state)
        if len(parts[0]) == 2:
            name = parts[0][1].strip()
            ret_type = object
        elif len(parts[0]) == 3:
            name = parts[0][2].strip()
            ret_type = get_type(parts[0][1], state, {}, True)
        else:
            throw_exception("Function first part must have only 2 arguments.", state)

        binarian_assert(is_name_unavailable(name, state), f"Function name is unavailiable : {name}.", state)

        args = []
        args_types = []
        if len(parts) > 1:
            for i in parts[1].replace("{", "").replace("}", "").split(","):
                i = i.split(":")
                if len(i) == 2: 
                    args.append(i[0].strip())
                    args_types.append(get_type(i[1].strip(), state, {}, True))
                elif len(i) == 1 and i[0].strip():
                    args.append(i[0].strip())
                    args_types.append(object)
                else:
                    throw_exception('Argument must have only one or fewer ":" and must have a name.', state)
                binarian_assert(is_name_unavailable(args[-1], state), f"Argument name is unavailiable : {args[-1]}.", state)

        op = Oper(OpIds.func, state.current_line, values=[name, *args], types=[ret_type, *args_types])
        op.oper = parse_block(state, state.current_line)
        return op

    elif lexic[0] == "return":
        op = Oper(OpIds.return_, state.current_line, get_args(lexic[1:], state))
        binarian_assert(len(op.args) != 1, "Return must have one argument.", state)
        return op

    else:
        return Oper(OpIds.call, state.current_line, [Oper(OpIds.variable, state.current_line, values=[lexic[0]])] + get_args(lexic[1:], state))
