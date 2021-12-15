#!/usr/bin/env python3

import pydot

import apps.examples.dice

from engine.app import app


if __name__ == '__main__':
    app.register()

    graph = pydot.Dot('FeatureCloud State Diagram', graph_type='digraph', bgcolor='transparent')

    for s in app.states:
        state = app.states[s]
        state_node = pydot.Node(state.name, label=state.name)
        if state.coordinator and state.participant:
            state_node.set('color', 'purple')
        elif state.coordinator:
            state_node.set('color', 'red')
        elif state.participant:
            state_node.set('color', 'blue')
        if state.name == 'initial' or state.name == 'terminal':
            state_node.set('peripheries', 2)
        graph.add_node(state_node)

    for t in app.transitions:
        transition = app.transitions[t]
        state_edge = pydot.Edge(transition[0].name, transition[1].name, label=t)
        if transition[2] and transition[3]:
            state_edge.set('color', 'purple')
        elif transition[3]:
            state_edge.set('color', 'red')
        elif transition[2]:
            state_edge.set('color', 'blue')
        graph.add_edge(state_edge)

    graph.write_png('output.png')
