import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict):
    feature: str
    design: str
    program: str
    qa: str

def design_node(state: State) -> State:
    state["design"] = "Design OK: interact with E near object"
    return state

def program_node(state: State) -> State:
    state["program"] = "Program OK: create IInteractable + PlayerInteractor"
    return state

def qa_node(state: State) -> State:
    state["qa"] = "QA OK: test range, null target, repeated press"
    return state

async def main():
    graph = StateGraph(State)

    graph.add_node("design", design_node)
    graph.add_node("program", program_node)
    graph.add_node("qa", qa_node)

    graph.set_entry_point("design")
    graph.add_edge("design", "program")
    graph.add_edge("program", "qa")
    graph.add_edge("qa", END)

    app = graph.compile()

    result = await app.ainvoke({
        "feature": "Player press E to interact",
        "design": "",
        "program": "",
        "qa": "",
    })

    print(result)

if __name__ == "__main__":
    asyncio.run(main())