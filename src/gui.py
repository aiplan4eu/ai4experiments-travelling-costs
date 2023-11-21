
import asyncio
import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum, auto
from networkx import Graph, dense_gnm_random_graph
from random import randint

import random
import logging
import os
import queue
import justpy as jp
# FOR FUTURE PROJECTS: check out the justpy.react functionality: https://justpy.io/blog/reactivity/


import unified_planning as up
from unified_planning.shortcuts import *



N_STARTING_LOCATIONS = 4
DEFAULT_EDGE_COST = 20
assert DEFAULT_EDGE_COST >= 0
BUTTON_CLASS = 'bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded m-2'

GRAPH_IMAGE_LOCATION = "/logos/generated/graph"
GRAPH_IMAGE_DIMENSIONS = "height: 400px; length: 400px;"

FIGSIZE = 8, 8
START_NODE_COLOR = "#02f414"
DESTINATION_NODE_COLOR = "#fd3a00"
NORMAL_NODE_COLOR = "#029cf4"
PATH_COLOR = "#f5fd00"
NODE_SIZE = 400
NODE_LABEL_FONT_SIZE = 8
EDGE_LABEL_FONT_SIZE = 8


class Mode(Enum):
    GENERATING_PROBLEM = auto()
    OPERATING = auto()


class Gui():
    def __init__(self):
        # a queue where the interface waits the start
        self.start_queue = queue.Queue()

        self.mode = Mode.GENERATING_PROBLEM
        self.graph = Graph()

        self.plan = None
        self.plan_cost = None
        self.plan_expected: bool = False
        self.image_id = 0

        self.plan_div: Optional[jp.Div] = None
        self.graph_image_div: Optional[jp.Img] = None

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.logger.setLevel(logging.INFO)

        assert N_STARTING_LOCATIONS > 1
        self.add_locations_to_graph(N_STARTING_LOCATIONS, display_graph=False)

        self.start = "L_1"
        self.destination = f"L_{N_STARTING_LOCATIONS}"

    def add_locations_to_graph(self, number_of_locations: int, display_graph: bool = True):
        assert number_of_locations > 0
        defined_locations = len(self.graph)
        locations_to_add = [f"L_{i}" for i in range(defined_locations+1, defined_locations+number_of_locations+1)]
        self.graph.add_nodes_from(((l, {"label": l}) for l in locations_to_add))

        last_defined_location = f"L_{defined_locations}" if defined_locations > 0 else None
        if last_defined_location is not None:
            self.graph.add_edge(last_defined_location, locations_to_add[0], weight=DEFAULT_EDGE_COST)
        self.graph.add_edges_from(zip(locations_to_add[:-1], locations_to_add[1:]), weight=DEFAULT_EDGE_COST)
        self.display_graph(True)

    def remove_locations_from_graph(self, number_of_locations: int):
        defined_locations = len(self.graph)
        assert number_of_locations > 0 and number_of_locations <= defined_locations
        locations_to_remove = [f"L_{i}" for i in range(defined_locations-number_of_locations+1, defined_locations+1)]
        self.graph.remove_nodes_from(locations_to_remove)
        if self.start not in self.graph:
            self.start = f"L_{random.randint(1, len(self.graph))}"
        if self.destination not in self.graph:
            self.destination = f"L_{random.randint(1, len(self.graph))}"
        self.display_graph(True)

    def randomize_graph_click(self, n_nodes, n_edges, min_cost, max_cost):
        random_graph = dense_gnm_random_graph(n_nodes, n_edges)
        nodes = [f"L_{i}" for i in range(1, n_nodes+1)]
        node_mapping = dict(zip(random_graph, nodes))
        self.graph = Graph()
        self.graph.add_nodes_from(nodes)
        for random_edge in random_graph.edges:
            edge = tuple(map(node_mapping.get, random_edge))
            # edge = (node_mapping.get(random_edge[0]), node_mapping.get(random_edge[1]))
            weight = randint(min_cost, max_cost)
            self.graph.add_edge(*edge, weight=weight)
        # self.graph.add_edges_from(map(lambda x: (node_mapping.get(x[0]), node_mapping.get(x[1])), random_graph.edges))
        self.start = f"L_{random.randint(1, len(self.graph))}"
        self.destination = f"L_{random.randint(1, len(self.graph))}"
        self.display_graph(True)

    def display_graph(self, reset_plan = False):
        if self.graph_image_div is None:
            return
        if reset_plan:
            self.plan = None
            self.plan_cost = None

        # from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        # self.graph_image_div.delete_components()
        # texts = [f"Locations: {', '.join(self.graph.nodes)}."]
        # texts.append(f"Start: {self.start}.")
        # texts.append(f"Destination: {self.destination}.")
        # for node, nbrdict in self.graph.adjacency():
        #     texts.append(f"{node} connected to: {', '.join(map(str, nbrdict.keys()))}.")

        # for t in texts:
        #     _ = jp.P(
        #         a=self.graph_image_div,
        #         text=t,
        #         classes=PLAN_PART_P_CLASS,
        #         style=PLAN_PART_P_STYLE,
        #     )
        # pos = nx.nx_agraph.graphviz_layout(self.graph, prog="twopi")
        scale_value = 1
        pos = nx.kamada_kawai_layout(self.graph, scale=scale_value)
        fig = plt.figure(figsize = FIGSIZE)
        ax = fig.add_subplot()
        color_map = {self.start: START_NODE_COLOR, self.destination: DESTINATION_NODE_COLOR}
        if self.plan is not None:
            path = set((str(ai.actual_parameters[1]) for ai in self.plan.actions[0:-1]))
            node_colors = [color_map.get(n, NORMAL_NODE_COLOR) if n not in path else PATH_COLOR for n in self.graph ]
        else:
            node_colors = [color_map.get(n, NORMAL_NODE_COLOR) for n in self.graph]

        nx.draw(self.graph, pos, with_labels=True, font_weight="bold", ax=ax, node_color=node_colors, font_size=NODE_LABEL_FONT_SIZE, node_size=NODE_SIZE)

        edge_labels = {(u, v): self.graph[u][v]["weight"] for u, v in self.graph.edges}
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, ax=ax, font_color='black', font_size=EDGE_LABEL_FONT_SIZE,)

        img_loc = f"{GRAPH_IMAGE_LOCATION}_{self.image_id}.png"
        self.image_id += 1
        fig.savefig(f".{img_loc}")

        self.graph_image_div.delete_components()

        _ = jp.Img(
            a=self.graph_image_div,
            src=f"static{img_loc}",
            style='max-width: 100%; height: auto;'
        )

    def reset_execution(self):
        self.mode = Mode.GENERATING_PROBLEM

    def update_planning_execution(self):
        from main_page import PLAN_PART_P_CLASS, PLAN_PART_P_STYLE
        if self.plan_div is not None:
            self.plan_div.delete_components()
            if self.plan is not None:
                _ = jp.P(
                    a=self.plan_div,
                    text=f"Found a sequence of moves that connects {self.start} to {self.destination}!",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
                for action_instance in self.plan.actions:
                    text = write_action_instance(action_instance)
                    _ = jp.P(
                        a=self.plan_div,
                        text=text,
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
                _ = jp.P(
                    a=self.plan_div,
                    text=f"After this sequence you arrived at: {self.destination}! The calculated cost is: {self.plan_cost}",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
            elif self.plan_expected:
                if self.mode == Mode.GENERATING_PROBLEM:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="No plan found; The start is not connected to the destination!",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
                else:
                    single_p = jp.P(
                        a=self.plan_div,
                        text="Wait for planning to finish!",
                        classes=PLAN_PART_P_CLASS,
                        style=PLAN_PART_P_STYLE,
                    )
            else:
                single_p = jp.P(
                    a=self.plan_div,
                    text="Modify graph and press NAVIGATE!",
                    classes=PLAN_PART_P_CLASS,
                    style=PLAN_PART_P_STYLE,
                )
            try:
                asyncio.run(self.plan_div.update())
            except RuntimeError:
                self.plan_div.update()
            self.display_graph()

    def clear_activities_click(self, msg):

        self.logger.info("Clearing")
        if self.mode == Mode.GENERATING_PROBLEM:
            self.graph = Graph()
            assert N_STARTING_LOCATIONS > 1
            self.add_locations_to_graph(N_STARTING_LOCATIONS)

            self.start = "L_1"
            self.destination = f"L_{N_STARTING_LOCATIONS}"

            self.plan_expected = False
            self.display_graph(True)
            self.update_planning_execution()

    def show_gui_thread(self):
        from main_page import main_page
        @jp.SetRoute("/")
        def get_main_page():
            return main_page(self)
        jp.justpy(get_main_page)

    def generate_problem_click(self, msg):
        self.logger.info("Generating")
        if self.mode == Mode.GENERATING_PROBLEM:
            self.mode = Mode.OPERATING
            self.plan = None
            self.plan_cost = None
            self.plan_expected = True
            self.update_planning_execution()
            # unlock the planing method with the problem correctly generated
            self.start_queue.put(None)


def write_action_instance(action_instance: up.plans.ActionInstance) -> str:
    return str(action_instance)

async def reload_page():
    for page in jp.WebPage.instances.values():
        if page.page_type == 'main':
            await page.reload()
