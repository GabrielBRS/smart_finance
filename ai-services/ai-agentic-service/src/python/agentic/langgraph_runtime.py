"""LangGraph adapter. One compile + one batch invoke per Mojo crossing.

Mojo owns agent policy, HTTP and use cases. This module only runs a graph
spec that Mojo already decided to offload.
"""

from __future__ import annotations

from typing import Any

from python._lazy import dump, installed, load, require


class LangGraphRuntime:
    def ping(self) -> str:
        return dump(
            {
                "backend": "langgraph",
                "installed": installed("langgraph"),
                "owner": "mojo",
            }
        )

    def run_batch(self, spec_json: str, inputs_json: str) -> str:
        spec = load(spec_json)
        inputs = load(inputs_json)
        if not isinstance(inputs, list):
            raise ValueError("inputs deve ser uma lista; uma travessia por lote")
        graph = self._compile(spec)
        results = [graph.invoke(item) for item in inputs]
        return dump(results)

    def _compile(self, spec: dict[str, Any]) -> Any:
        require("langgraph")
        from langgraph.graph import END, START, StateGraph

        nodes = spec.get("nodes") or []
        edges = spec.get("edges") or []
        entry = spec.get("entry") or (nodes[0]["id"] if nodes else None)
        if not entry:
            raise ValueError("graph spec sem entry/nodes")

        builder = StateGraph(dict)
        for node in nodes:
            node_id = node["id"]
            builder.add_node(node_id, _passthrough)
        for edge in edges:
            builder.add_edge(edge[0], edge[1])
        builder.add_edge(START, entry)
        if nodes:
            builder.add_edge(nodes[-1]["id"], END)
        return builder.compile()


def _passthrough(state: dict[str, Any]) -> dict[str, Any]:
    return state
