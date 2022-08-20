from typing import Optional, Dict

from funcs.utils import check_args
from parsing.oper import Oper

def and_keyword(op : Oper, state, local : Optional[Dict[str, object]]) -> int:
    arg1, arg2 = check_args(op, [object, object], state, local)

    return int(arg1 and arg2)

def or_keyword(op : Oper, state, local : Optional[Dict[str, object]]) -> int:
    arg1, arg2 = check_args(op, [object, object], state, local)

    return int(arg1 or arg2)

def not_keyword(op : Oper, state, local : Optional[Dict[str, object]]) -> int:
    arg = check_args(op, [object], state, local)[0]

    return int(not arg)