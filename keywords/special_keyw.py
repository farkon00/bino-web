import sys

from typing import Optional, Dict

from importlib.abc import MetaPathFinder
from funcs.exceptions import binarian_assert, throw_exception
from funcs.utils import check_args, type_to_str
from bin_types.list import List
from parsing.oper import Oper


# Fobiding for pyeval to import os
class ForbiddenModules(MetaPathFinder):
    RESTRICTED_MODULES = ["os", "commands", "subprocess", "pty", "platform", "pdb", "pip"]
    def __init__(self):
        super().__init__()

    def find_spec(self, fullname, path, target=None):
        if fullname in self.RESTRICTED_MODULES:
            raise ImportError("Can't import restricted module in online mode")
sys.meta_path.insert(0, ForbiddenModules())

class DummySys:
    def __init__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.stdin = sys.stdin
        self.argv = sys.argv

def convert_keyword(op : Oper, state, local : Optional[Dict[str, object]]):
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

def pyeval_keyword(op : Oper, state, local : Optional[Dict[str, object]]):
    code, imports, exports = check_args(op, [List, List, List], state, local)

    glob = {i : (list(j) if isinstance(j, List) else j) for i, j in imports}
    glob = {**glob, "throw_exception" : throw_exception, "state" : state}

    for i in ForbiddenModules.RESTRICTED_MODULES:
        try:
            del sys.modules[i]
        except KeyError: pass

    real_sys = sys

    sys.modules["sys"] = DummySys()

    try:
        exec("def open(*args): raise Exception(\"can't open a file in online mode\")\n" + "\n".join(code), glob)
    except Exception as e:
        throw_exception(f"Python exception occured : {e}", state)

    # Clean up sandbox
    sys.modules["sys"] = real_sys

    ret = []
    for i in exports:
        binarian_assert(i not in glob, f"Variable {i} was not found", state)
        ret.append(glob[i])

    if state.is_expr:
        return List.convert_lists(ret)