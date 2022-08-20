from typing import Iterable, Optional, Dict
from bin_types.function import Function
from funcs.exceptions import binarian_assert
from funcs.utils import check_args
from parsing.oper import Oper

def func_keyword(op : Oper, state, in_vars : Dict[str, object], is_func : bool):
    binarian_assert(state.is_expr, "This operation is unavailable in expressions.", state)
    binarian_assert(is_func, "Cant define function inside other function.", state)

    in_vars[op.values[0]] = Function(op)

def call_keyword(op : Oper, state, local : Optional[Dict[str, object]]):
    func_args : list = check_args(op, [Function], state, local)
    if isinstance(func_args, Iterable):
        args = func_args[1:]
        func : Function = func_args[0]
    else:
        func = func_args
        args = []

    binarian_assert(len(func.args) > len(args), f"You didn`t give enough arguments,\
{len(func.args)} was expected, {len(args)} found.", state)
    binarian_assert(len(func.args) < len(args), f"You gave too much arguments,\
{len(func.args)} was expected, {len(args)} found.", state)

    call_line = state.current_line

    state.call_stack.append((func.name, state.current_line))

    ret = func.execute(args, state)

    del state.call_stack[-1]
    state.current_line = call_line

    return ret

def return_keyword(op : Oper, state, is_func : bool, local : Optional[Dict[str, object]]):
    binarian_assert(not is_func, 'Keyword "return" is restricted out of functions.', state)

    state.last_return = check_args(op, [object], state, local)[0]