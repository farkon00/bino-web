from .oper import *

from bin_types.list import List

from funcs.exceptions import binarian_assert, throw_exception
from funcs.brackets_parser import parse_lexic

def get_args(lexic, state) -> list[Oper]:
    """
    Parses literal, variable or expression and returns list of Oper object 
    """

    ret = []
    lexic = parse_lexic(lexic, state)

    for var in lexic:
        if var[0] == "[": # list parsing
            elems = get_args(var[1:-1].split(), state)
            ret.append(Oper(OpIds.value, state.current_line, values=[List(elems)]))

        elif var[0] == '"': # string parsing
            ret.append(Oper(OpIds.value, state.current_line, values=[parse_string(var, state)]))

        elif var.lower().startswith("0x") or\
         var.lower().startswith("-0x"): # Hex numbers
            binarian_assert(any(i not in "0123456789abcdef" for i in var[2:].lower()),
             f"Invalid hexadecimal litteral: {var}", state)
            ret.append(Oper(OpIds.value, state.current_line, values=[int(var, 16)]))

        elif var.lower().startswith("0b") or\
         var.lower().startswith("-0b"): # Binary numbers
            binarian_assert(any(i not in "01" for i in var[2:].lower()),
             f"Invalid binary litteral: {var}", state)
            ret.append(Oper(OpIds.value, state.current_line, values=[int(var, 2)]))

        elif var.lower().startswith("0o") or\
         var.lower().startswith("-0b"): # Octal numbers
            binarian_assert(any(i not in "01234567" for i in var[2:].lower()),
             f"Invalid octal litteral: {var}", state)
            ret.append(Oper(OpIds.value, state.current_line, values=[int(var, 8)]))

        elif var.isdigit() or\
         (var[0] == "-" and var[1:].isdigit()): # int parsing
            ret.append(Oper(OpIds.value, state.current_line,
             values=[int(var)]))

        elif var.replace(".", "").isdigit() or (var[0] == "-" and\
         var[1:].replace(".", "").isdigit()): # float parsing
            ret.append(Oper(OpIds.value, state.current_line,
             values=[float(var)]))

        elif var[0] == "(": # expression parsing
            ret.append(state.GLOBAL_FUNCS["parse_line"](var[1:-1], state))

        else: # variable parsing
            ret.append(Oper(OpIds.variable, state.current_line, values=[var]))

    return ret

def parse_string(var : str, state) -> str:
    res = ""
    escaped = False
    for i in var[1:-1]:
        if escaped:
            if i == "n": char = "\n"
            if i == "t": char = "\t"
            if i == "r": char = "\r"
            if i == "\"": char = "\""
            if i == "\\": char = "\\"
            else: throw_exception(f"Unknown escape sequence: \\{i}", state)
            escaped = False
        elif i == "\\":
            escaped = True
            char = ""
        else:
            char = i

        res += char

    return res