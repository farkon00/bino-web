from io import TextIOWrapper
from .oper import Oper, OpIds
from subprocess import run

class AstRenderingState:
    def __init__(self, out : TextIOWrapper):
        self.last_node = 0
        self.last_block = 0

        self.out = out

def render_ast(ops : list[Oper], name : str) -> None:
    name = ".".join(name.split(".")[:-1])
    with open(name + ".dot", "w") as out:
        state = AstRenderingState(out)
        out.write("digraph AST {\n")
        
        for op in ops:
            render_node(state, op)

        out.write("}\n")
    run((f"dot -Tsvg {name}.dot -o {name}.svg"))    

def render_node(state : AstRenderingState, op : Oper) -> int:
    state.last_node += 1
    my_node = state.last_node
    skip_args = 0
    if op.id == OpIds.value | OpIds.variable:
        if isinstance(op.values[0], list):
            state.out.write(f"Node{my_node} [label=\"List\"]\n")
            for i in op.values[0]:
                state.out.write(f"Node{my_node} -> Node{render_node(state, i)} [arrowhead=dot];\n")
        else:
            state.out.write(
                f"Node{my_node} [label=\"{op.values[0] if not isinstance(op.values[0], list) else 'listy'}\" shape=none];\n"
            )

    elif op.id == OpIds.operation:
        state.out.write(
            f"Node{my_node} [label=\"{op.values[0]}\"];\n"
        )

    elif op.id == OpIds.call:
        skip_args = 1
        state.out.write(
            f"Node{my_node} [label=\"{op.args[0].values[0]}\"];\n"    
        )
    
    else:
        label = str(op.id).removeprefix('OpIds.').removesuffix('_') + "\\n"
        label += '\\n'.join([str(i) for i in op.values])

        state.out.write(
            f"Node{my_node} [label=\"{label}\" shape=box];\n"
        )

    for i in op.args[skip_args:]:
        new_node = render_node(state, i)
        state.out.write(f"Node{my_node} -> Node{new_node} [arrowhead=box];\n")

    if op.oper:
        state.last_block += 1
        state.out.write("subgraph cluster_%i {\n" % state.last_block)

        for i in op.oper:
            new_node = render_node(state, i)
            state.out.write(f"Node{my_node} -> Node{new_node};\n")

        state.out.write("style=dotted;\n")
        state.out.write("}\n")
        
    return my_node 