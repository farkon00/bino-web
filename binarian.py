import sys
import pickle

from time import time
from posixpath import abspath
from typing import Callable, Optional, Dict
from typing import List as ListType

from parsing.parsing import *
from parsing.graph_ast import *

from type_checking import *

from funcs.code_preparer import *
from funcs.exceptions import *

from keywords import *

class ExecutionState:
    """Class that contains all data about execution state and constants for execution"""
    def __init__(self, code : str) -> None:
        self.vars : Dict[str, object] = {}
        self.is_expr : bool = False

        self.current_line : int = -1

        self.opened_ifs : ListType[bool] = []

        self.call_stack : ListType[tuple[str, int]] = [] # func_name, line
        self.last_return : object = None 
        self.is_breaked : bool = False
        self.is_continued: bool = False

        self.code : str = code
        self.lines : ListType[str] = code.split("\n")
        self.std_lines : int = 0 # Shold be setted to right value in main 
        self.std_lib_vars : Dict[str, object] = {} 

        self.input_time : int = 0

        self.types : Dict[str, type] = {
            "object" : object,
            "int" : int,
            "float" : float,
            "str" : str,
            "function" : Function,
            "list" : List,
        }

        self.operations : ListType[str] = [
            "+", "-", "*", "/", "**", "%", ">", "<", ">=", "<=", "==", "!="
        ]
        self.iter_operations : tuple[str, str, str] = (
            "+", "==", "!="
        ) 
        self.diff_types_operations : tuple[str, str] = (
            "==", "!="
        )

        self.RESTRICTED_NAMES : ListType[str] = [
            "and", "or", "not", "var", "drop", "input", "func",
            "return", "index", "append", "zip", "for", "while", "if",
            "elif", "else", "object", "int", "float", "list", "function",
            "break", "continue",
            *self.operations
        ]
        self.BRACKETS : ListType[str] = ["(", ")", "[", "]", "{", "}"]
        self.GLOBAL_FUNCS : Dict[str, Callable] = {
            "execute_line" : execute_line,
            "execute_opers" : execute_opers,
            "parse_line" : parse_line
        }

def execute_line(op : Oper, state : ExecutionState, local : Optional[Dict[str, object]], is_expr : bool = True) -> object:
    """Executes one operation"""
    state.current_line = op.line

    if state.is_breaked:
        state.current_line -= 1 # To show previous line with break in exception
        throw_exception("Break is restricted out of loops", state)

    if state.is_continued:
        state.current_line -= 1 # To show previous line with continue in exception
        throw_exception("Continue is restricted out of loops", state)

    is_func = local != None
    full_vars = {**state.vars, **(local if local else {})}
    state.is_expr = is_expr 

    if op.id not in (OpIds.else_, OpIds.elif_) and not state.is_expr and state.opened_ifs:
        del state.opened_ifs[-1]

    if op.id == OpIds.variable:
        binarian_assert(op.values[0] not in full_vars, f"Variable {op.values[0]} is not defined", state)
        return full_vars[op.values[0]]
    elif op.id == OpIds.value:
        ret = op.values[0]
        if isinstance(ret, list):
            res = List()
            for i in ret:
                res.append(execute_line(i, state, local))
            return res
        else:
            return ret
    elif op.id == OpIds.operation:
        return execute_oper(op, state, local)
    elif op.id == OpIds.var:
        var_keyword(op, state, local if local is not None else state.vars, local)
    elif op.id == OpIds.drop:
        drop_keyword(op, state, local if local is not None else state.vars)
    elif op.id == OpIds.input:
        return input_keyword(op, state)
    elif op.id == OpIds.convert:
        return convert_keyword(op, state, local)
    elif op.id == OpIds.pyeval:
        return pyeval_keyword(op, state, local)
    elif op.id == OpIds.and_:
        return and_keyword(op, state, local)
    elif op.id == OpIds.or_:
        return or_keyword(op, state, local)
    elif op.id == OpIds.not_:
        return not_keyword(op, state, local)
    elif op.id == OpIds.index:
        return index_keyword(op, state, local)
    elif op.id == OpIds.setindex:
        return setindex_keyword(op, state, local)
    elif op.id == OpIds.append:
        return append_keyword(op, state, local)
    elif op.id == OpIds.if_:
        if_keyword(op, state, local)
    elif op.id == OpIds.else_:
        else_keyword(op, state, local)
    elif op.id == OpIds.elif_:
        elif_keyword(op, state, local)
    elif op.id == OpIds.for_:
        for_keyword(op, state, local)
    elif op.id == OpIds.while_:
        while_keyword(op, state, local)
    elif op.id == OpIds.break_:
        break_keyword(op, state)
    elif op.id == OpIds.continue_:
        continue_keyword(op, state)
    elif op.id == OpIds.func:
        func_keyword(op, state, local if local is not None else state.vars, is_func)
    elif op.id == OpIds.return_:
        return return_keyword(op, state, is_func, local)
    elif op.id == OpIds.call:
        return call_keyword(op, state, local)
    else:
        assert False, "Unreachable" 
    
    return None

def execute_opers(opers : ListType[Oper], state : ExecutionState, local : Optional[Dict[str, object]],
 main : bool = False, is_loop : bool = False) -> None:
    """Executes list of operations"""
    for i in opers:
        if state.current_line < state.std_lines and main:
            state.std_lib_vars = state.vars.copy()

        execute_line(i, state, local, is_expr=False)

        if state.last_return is not None:
            return

        if is_loop:
            if state.is_breaked:
                break

            if state.is_continued:
                state.is_continued = False
                break

def main(test_argv : ListType[str] = None, program: str = None) -> None:
    start_time = time()

    if test_argv:
        argv = test_argv
    else:
        argv = sys.argv

    if ("--help" in argv or len(argv) < 2) and program is None:
        print(help_string)
        exit(0)

    try:
        if "-load-cache" not in argv and program is None:
            code = open(argv[1], "r", encoding="utf-8").read()
        elif program is not None:
            code = program
        else:
            ops = pickle.load(open(argv[1], "rb"))
    except Exception:
        print(f"File not found {abspath(argv[1])}")
        exit(1)

    if "-no-std" not in argv:
        try:
            std_path = "\\".join(__file__.split("\\")[:-1])
            std_path += "\\" if std_path else ""
            std_path += "std.bino"
            
            try:
                std_lib = open(std_path, "r").read()
            except FileNotFoundError:
                std_lib = open("std.bino", "r").read()
        except FileNotFoundError:
            print("\nSTD LIBRARY FILE WAS NOT FOUND!")
            print(f"Path where std library was excepted {std_path} and your current directory\n\n")
            std_lib = ""
    else:
        std_lib = ""

    state = ExecutionState(code if "-load-cache" not in argv else "")
    state.std_lines = std_lib.count("\n") + 1

    if "-load-cache" not in argv:
        code = delete_comments(std_lib + "\n" + code)
        state = ExecutionState(code if "-load-cache" not in argv else "")
        state.std_lines = std_lib.count("\n") + 1
        ops = parse_to_ops(state)

    if "-cache" in argv and "-load-cache" not in argv:
        with open(f"{argv[1]}.binc", "wb") as f:
            pickle.dump(ops, f)

        print("Seccessfully parsed and cached.")
        exit(0)

    if "-opers" in argv:
        render_ast(ops, argv[1])

    if "-tc" in argv:
        type_check(ops, state)

    execute_opers(ops, state, None, main=True)

    if "-d" in argv:
        debug_vars = list(state.vars.items())
        for i in state.std_lib_vars.items():
            debug_vars.remove(i)
        
        print("\n" + str({i : str(j) for i, j in debug_vars}))

    print(f"\nFinished in {time() - start_time - state.input_time} sec")
        
help_string =\
"""
Usage: binarian <file> [options]

Options:

    -d          Debug mode, outputs variables values at the end of execution. 

    -tc         Type check code before executing, will output all errors found.

    -no-std     Disables std library.

    -cache      Caches parsed code to file. 

    -load-cache Sets mode to loading cached file.

    -opers      Creates .dot and .svg file with graphviz representing ast and all operations parsed

    --help      Show this message.
"""

if __name__ == "__main__":
    main()
