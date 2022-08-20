from typing import List

from funcs.brackets_parser import *
from funcs.exceptions import *
from parsing.oper import Oper

class Function:
    """Class that represents function in binarian"""

    def __init__(self, oper : Oper):
        self.body = oper.oper
        self.args = oper.values[1:]
        self.name = oper.values[0]

    def execute(self, args : List[str], state) -> object:
        """Executes function"""
        is_expr_before = state.is_expr
        state.is_expr = False

        local = {self.args[j] : args[j] for j in range(len(args))}
        state.GLOBAL_FUNCS["execute_opers"](self.body, state, local)

        # Stops function and returns return value on return
        if state.last_return != None:
            state.is_expr = is_expr_before

            ret = state.last_return
            state.last_return = None

            return ret
        else:
            return 0

    def __str__(self):
        return f"<function : {' '.join(self.args)}>"