from typing import Optional

from bin_types.list import List
from funcs.exceptions import binarian_assert
from funcs.utils import type_to_str
from parsing.oper import Oper

def execute_oper(op : Oper, state, local : Optional[dict[str, object]]):
    operation = op.values[0]
    types = (int, float, str, List)
    arg1 = state.GLOBAL_FUNCS["execute_line"](op.args[0], state, local)
    arg2 = state.GLOBAL_FUNCS["execute_line"](op.args[1], state, local)
    binarian_assert(not isinstance(arg1, types) and not isinstance(arg2, types) and (operation not in state.diff_types_operations),
        f"Invalid types for operation {operation}", state)

    if isinstance(arg1, str | List) or isinstance(arg2, str | List):
        binarian_assert(type(arg1) != type(arg2) and op.values[0] not in state.diff_types_operations, 
            f"Cant perform operation with different types : {type_to_str(type(arg1))} and {type_to_str(type(arg2))}", state
        )
        binarian_assert(operation not in state.iter_operations, 
            f"Cant perform \"{operation}\" on {type_to_str(type(arg1))} and {type_to_str(type(arg2))}", state
        )

    if operation == "+":    return     arg1 + arg2 if not isinstance(arg1, List) else List(arg1 + arg2)
    elif operation == "-":  return     arg1 - arg2
    elif operation == "*":  return     arg1 * arg2
    elif operation == "/":  return     arg1 / arg2  
    elif operation == "**": return     arg1 ** arg2
    elif operation == "%":  return     arg1 % arg2
    elif operation == "==": return int(arg1 == arg2)
    elif operation == "!=": return int(arg1 != arg2)
    elif operation == ">":  return int(arg1 > arg2)
    elif operation == "<":  return int(arg1 < arg2)
    elif operation == ">=": return int(arg1 >= arg2)
    elif operation == "<=": return int(arg1 <= arg2)

    assert False, "Unreachable, operation not found"