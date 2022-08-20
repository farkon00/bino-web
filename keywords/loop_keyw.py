from typing import Optional, Dict

from funcs.exceptions import binarian_assert
from funcs.utils import type_to_str
from bin_types.list import List
from parsing.oper import Oper

def break_keyword(op : Oper, state):
    state.is_breaked = True

def continue_keyword(op : Oper, state):
    state.is_continued = True

def for_keyword(op : Oper, state, local : Optional[Dict[str, object]]):
    binarian_assert(state.is_expr, "This operation is unavailable in expressions.", state)

    var_name = op.values[0]
    list_ = state.GLOBAL_FUNCS["execute_line"](op.args[0], state, local)
    binarian_assert(not isinstance(list_, List | str), f"Cant iterate throw {type_to_str(type(list_))}.", state)
    for loop_iter in list_:
        if local is not None:
            local[var_name] = loop_iter
        else:
            state.vars[var_name] = loop_iter

        state.current_line = op.line

        state.GLOBAL_FUNCS["execute_opers"](op.oper, state, local, is_loop=True)

        if state.is_breaked:
            state.is_breaked = False
            state.current_line = op.oper[-1].line
            break

        if state.last_return != None:
            break

def while_keyword(op : Oper, state, local : Optional[Dict[str, object]]):
    binarian_assert(state.is_expr, "This operation is unavailable in expressions.", state)


    while True:
        if not state.GLOBAL_FUNCS["execute_line"](op.args[0], state, local):
            break

        state.GLOBAL_FUNCS["execute_opers"](op.oper, state, local, is_loop=True)

        if state.is_breaked:
            state.is_breaked = False
            state.current_line = op.oper[-1].line
            break

        if state.last_return != None:
            break

    state.current_line = op.oper[-1].line