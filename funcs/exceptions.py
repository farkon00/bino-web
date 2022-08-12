from sys import exit, argv

def throw_exception(text : str, state, display_line : bool = True):
    """
    Throws binarina exception with binarian call stack
    Cant be handeled by try-except block
    If display_line is False, it wont print call stack 
    """
    exc_text = f"\nWhile {'executing code' if 'TypeCheck' not in str(type(state)) else 'type checking'}, exception was thrown :\n\n"

    if display_line:
        for j, i in enumerate(state.call_stack):
            exc_text += f"line {i[1] + 1 - state.std_lines} "
            if j > 0:
                exc_text += f"in {state.call_stack[j-1][0]} "
            exc_text += ":\n"

            clear_text = " ".join(state.lines[i[1]].split()) 
            exc_text += "  " + clear_text + "\n"

        exc_text += f"line {state.current_line + 1 - state.std_lines} "
        if state.call_stack:
            exc_text += f"in {state.call_stack[-1][0]} "
        exc_text += ":\n"

        clear_text = " ".join(state.lines[state.current_line].split()) 
        exc_text += "  " + clear_text + "\n"

    exc_text += "\n" + text

    print(exc_text)

    if "-d" in argv:
        debug_vars = list(state.vars.items())
        for i in state.std_lib_vars.items():
            debug_vars.remove(i)
        
        print("\n" + str({i : str(j) for i, j in debug_vars}))

    exit(1)

def binarian_assert(condition : bool, text : str, state, display_line : bool = True):
    """
    If condition is true throws binarian error
    If display_line is False, it wont print call stack 
    !WARNING!
    Works opposite to regular asserts, THROWS EXCEPTION ON TRUE 
    """
    if condition:
        throw_exception(text, state, display_line=display_line)