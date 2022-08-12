import traceback as tb
from funcs.exceptions import binarian_assert, throw_exception
from funcs.utils import check_args, type_to_str
from bin_types.list import List
from parsing.oper import Oper

def convert_keyword(op : Oper, state, local : dict[str, object] | None):
    original = state.GLOBAL_FUNCS['execute_line'](op.args[0], state, local)
    end_type = op.values[0]

    if isinstance(original, type) and issubclass(end_type, str):
        return type_to_str(original)

    try:
        final = end_type(original)
    except Exception:
        throw_exception(f"Can`t convert to type {type_to_str(end_type)}", state)

    if state.is_expr:
        return final

def pyeval_keyword(op : Oper, state, local : dict[str, object] | None):
    code, imports, exports = check_args(op, [List, List, List], state, local)

    glob = {i : (list(j) if isinstance(j, List) else j) for i, j in imports}
    glob = {**glob, "throw_exception" : throw_exception, "state" : state}
    try:
        exec("\n".join(code), glob)
    except Exception as e:
        throw_exception(f"Python exception occured : {e}", state)

    ret = []
    for i in exports:
        binarian_assert(i not in glob, f"Variable {i} was not found", state)
        ret.append(glob[i])

    if state.is_expr:
        return List.convert_lists(ret)