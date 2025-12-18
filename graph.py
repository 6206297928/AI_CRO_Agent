from langgraph.graph import StateGraph
from agents.data_agent import data_agent
from agents.funnel_agent import funnel_agent
from agents.memory_agent import memory_agent
from agents.cro_reasoning_agent import cro_reasoning_agent
from agents.experiment_agent import experiment_agent

def build_cro_graph():
    graph = StateGraph(dict)

    graph.add_node("data", data_agent)
    graph.add_node("funnel", funnel_agent)
    graph.add_node("memory", memory_agent)
    graph.add_node("cro", cro_reasoning_agent)
    graph.add_node("experiment", experiment_agent)

    graph.set_entry_point("data")

    graph.add_edge("data", "funnel")
    graph.add_edge("funnel", "memory")
    graph.add_edge("memory", "cro")
    graph.add_edge("cro", "experiment")

    return graph.compile()

