from functools import partial
# Description of the component saved here.
# This is the travelling-costs component. It allows the user to create a map with distances between the locations.

# After the user is satisfied with the created map and has set the starting point and the destination he can click NAVIGATE the map and the best route from the start to the end will be highlighted.

# Under the hood the component creates a unified-planning Problem and sends it to another component to be solved; then displays (both graphically and textually) the returned plan with the associated total distance.


import justpy as jp

from gui import Gui, Mode

LEFT_MARGIN, RIGHT_MARGIN = " margin-left: 10px; ", " margin-right: 20px; "

TITLE_DIV_CLASS = "grid justify-between gap-2 grid-cols-3"
TITLE_DIV_STYLE = "grid-template-columns: auto auto auto; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN

TITLE_TEXT_DIV_STYLE = "font-size: 80px; text-align: center; text-weight: bold;"

DESCRIPTION_STYLE = "margin-top: 15px; font-size: 16px;" + LEFT_MARGIN + RIGHT_MARGIN
DESCRIPTION_TEXT = """
Travelling-costs demo: this demo allows you to create and navigate a map with specified distances on the connections.
The text to the left of the buttons specifies the precise behavior of the button itself:
 * Add Locations(N): adds N locations to the map, in numerical order.
 * Remove Locations(N): removes the last N locations from the map; if the start/destination is one of those it will be randomly reassigned.
 * Add Connection(N, M, D): adds the connection between the L_N and L_M and assigns the distance D.
 * Remove Connection(N, M): removes the connection between L_N and L_M.
 * Set Start(N): sets L_N as the starting location; the starting location is represented in GREEN.
 * Set Destination(N): sets L_N as the destination; the destination is represented in RED.
 * Randomize Graph(N, M, MinD, MaxD): creates a new map with N locations, M random connections with random distances in [MinD, MaxD], a random Start and a random Destination.
 * RESET: restores the map to it's initial configuration.
 * NAVIGATE: prints a plan to go from the starting location to the destination; following the given map and minimizing the distance.
"""
SINGLE_DESCRIPTION_STYLE = LEFT_MARGIN + RIGHT_MARGIN


MAIN_BODY_DIV_CLASS = "grid justify-between grid-cols-3 gap-7"
MAIN_BODY_DIV_STYLE = "grid-template-columns: max-content minmax(200px, 45%) 0.9fr; column-gap: 15px; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN
# MAIN_BODY_DIV_STYLE = "grid-template-columns: minmax(max-content, 25%) minmax(max-content, 25%) 10px minmax(max-content, 33%); width: 100vw; margin-top: 15px;" + LEFT_MARGIN + RIGHT_MARGIN

ACTIONS_DIV_CLASS = "grid"
# Setting height to 0 it'sa trick to solve the problem of the goal div changing size
ACTIONS_DIV_STYLE = f"grid-template-columns: auto auto; font-size: 30px; font-weight: semibold; height: 0px;"

TEXT_WIDTH = 230 # px
COL_GAP = 4 #px
TEXT_INPUT_P_STYLE_COMMON = "font-weight: normal; font-size: 20px; margin-top: 15px; border: 0.9px solid #000; background-color: #e1eff7; padding: 5px; margin-bottom: 17px; width: "
TEXT_INPUT_P_CLASS = ""
TEXT_INPUT_P_STYLE = f"{TEXT_INPUT_P_STYLE_COMMON}{TEXT_WIDTH}px;"

DOUBLE_SLOT_DIV_CLASS = "flex grid-cols-2"
DOUBLE_SLOT_DIV_STYLE = f"column-gap: {COL_GAP}px;"

DOUBLE_TEXT_INPUT_P_CLASS = ""
DOUBLE_TEXT_INPUT_P_STYLE = f"{TEXT_INPUT_P_STYLE_COMMON}{int((TEXT_WIDTH-COL_GAP)/2)}px;"

TRIPLE_SLOT_DIV_CLASS = "flex grid-cols-3"
TRIPLE_SLOT_DIV_STYLE = f"column-gap: {COL_GAP}px;"

TRIPLE_TEXT_INPUT_P_CLASS = ""
TRIPLE_TEXT_INPUT_P_STYLE = f"{TEXT_INPUT_P_STYLE_COMMON}{int((TEXT_WIDTH-2*COL_GAP)/3)}px;"

QUADRUPLE_SLOT_DIV_CLASS = "flex grid-cols-4"
QUADRUPLE_SLOT_DIV_STYLE = f"column-gap: {COL_GAP}px;"

QUADRUPLE_TEXT_INPUT_P_CLASS = ""
QUADRUPLE_TEXT_INPUT_P_STYLE = f"{TEXT_INPUT_P_STYLE_COMMON}{int((TEXT_WIDTH-3*COL_GAP)/4)}px;"

ADD_BUTTON_CLASS = "bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded m-2"
ADD_BUTTON_STYLE = f"font-weight: semibold; font-size: 20px; width: {TEXT_WIDTH}px; margin-top: 5px;"

GOALS_DIV_CLASS = ""
GOALS_DIV_STYLE = "font-size: 30px; font-weight: semibold;"

GOALS_CONTAINER_DIV_CLASS = ""
GOALS_CONTAINER_DIV_STYLE = ""

CLEAR_SOLVE_BUTTONS_CLASS = ADD_BUTTON_CLASS
CLEAR_SOLVE_BUTTONS_STYLE = "font-weight: semibold; font-size: 20px;"

PLAN_DIV_CLASS = ""
PLAN_DIV_STYLE = f"font-size: 30px; font-weight: semibold;"

PLAN_PART_P_CLASS = ""
PLAN_PART_P_STYLE = f"font-weight: normal; font-size: 18px;"


def main_page(gui: Gui):
    wp = jp.WebPage(delete_flag = False)
    wp.page_type = 'main'
    title_div = jp.Div(
        a=wp,
        classes=TITLE_DIV_CLASS,
        style=TITLE_DIV_STYLE,
    )
    fbk_logo_div = jp.Div(
        a=title_div,
        # text="FBK LOGO",
        # style="font-size: 30px;",
        style="height: 160px;",
    )
    fbk_logo = jp.Img(
        src="/static/logos/fbk.png",
        a=fbk_logo_div,
        classes="w3-image",
        # style="height: 100%; length: auto;",
    )
    title_text_div = jp.Div(
        a=title_div,
        text="TRAVELLING-COSTS",
        style=TITLE_TEXT_DIV_STYLE,
    )
    unified_planning_logo_div = jp.Div(
        a=title_div,
        style="height: 160px;",
    )
    unified_planning = jp.Img(
        src="/static/logos/unified_planning_logo.png",
        a=unified_planning_logo_div,
        classes="w3-image",
        style="max-width: 100%; height: 160px;"
    )

    description_div = jp.Div(
        a=wp,
        style=DESCRIPTION_STYLE,
    )
    for single_desc in DESCRIPTION_TEXT.split("\n"):
        description_paragraph = jp.P(
            a=description_div,
            style=SINGLE_DESCRIPTION_STYLE,
            text=single_desc,
        )

    main_body_div = jp.Div(
        a=wp,
        classes=MAIN_BODY_DIV_CLASS,
        style=MAIN_BODY_DIV_STYLE,
    )

    actions_div = jp.Div(
        a=main_body_div,
        text="ACTIONS:",
        classes=ACTIONS_DIV_CLASS,
        style=ACTIONS_DIV_STYLE,
    )

    # Useless paragprah, added just as a place-holder
    _ = jp.P(
        a=actions_div,
        text="",
    )

    # Add Locations
    ADD_LOCATIONS_TEXT_PLACEHOLDER = ""
    add_locations_text = jp.Input(
        a=actions_div,
        placeholder= ADD_LOCATIONS_TEXT_PLACEHOLDER,
        classes=TEXT_INPUT_P_CLASS,
        style=TEXT_INPUT_P_STYLE,
    )
    add_locations_button = jp.Input(
        a=actions_div,
        value="Add Locations",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    def add_locations_button_click(add_locations_text: jp.Input, gui: Gui, component, msg):
        text = add_locations_text.value
        gui.logger.info("Clicked add_locations: " + text + f"with mode: {gui.mode}")
        try:
            value = int(text)
            if value > 0:
                add_locations_text.value = ADD_LOCATIONS_TEXT_PLACEHOLDER
                if gui.mode == Mode.GENERATING_PROBLEM:
                    gui.add_locations_to_graph(value)
            else:
                add_locations_text.value = "Err: <= 0"
        except ValueError:
            add_locations_text.value = "Err: NAN"
    add_locations_button.on('click', partial(add_locations_button_click, add_locations_text, gui))

    # Remove Locations
    REMOVE_LOCATIONS_TEXT_PLACEHOLDER = ""
    remove_locations_text = jp.Input(
        a=actions_div,
        placeholder= REMOVE_LOCATIONS_TEXT_PLACEHOLDER,
        classes=TEXT_INPUT_P_CLASS,
        style=TEXT_INPUT_P_STYLE,
    )
    remove_locations_button = jp.Input(
        a=actions_div,
        value="Remove Locations",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    def remove_locations_button_click(remove_locations_text: jp.Input, gui: Gui, component, msg):
        text = remove_locations_text.value
        gui.logger.info("Clicked remove_locations: " + text + f"with mode: {gui.mode}")
        try:
            graph = gui.graph
            defined_locations = len(graph)
            value = int(text)
            if value > 0:
                if value <= defined_locations:
                    remove_locations_text.value = REMOVE_LOCATIONS_TEXT_PLACEHOLDER
                    if gui.mode == Mode.GENERATING_PROBLEM:
                        gui.remove_locations_from_graph(value)
                else:
                    remove_locations_text.value = f"Err: > {defined_locations}"
            else:
                remove_locations_text.value = "Err: <= 0"
        except ValueError:
            remove_locations_text.value = "Err: NAN"
    remove_locations_button.on('click', partial(remove_locations_button_click, remove_locations_text, gui))

    # Add Connection
    ADD_CONNECTION_TEXT_PLACEHOLDER = ""
    add_connection_text_div = jp.Div(
        a=actions_div,
        classes=TRIPLE_SLOT_DIV_CLASS,
        style=TRIPLE_SLOT_DIV_STYLE,
    )
    add_connection_text_1 = jp.Input(
        a=add_connection_text_div,
        placeholder= ADD_CONNECTION_TEXT_PLACEHOLDER,
        classes=TRIPLE_TEXT_INPUT_P_CLASS,
        style=TRIPLE_TEXT_INPUT_P_STYLE,
    )
    add_connection_text_2 = jp.Input(
        a=add_connection_text_div,
        placeholder= ADD_CONNECTION_TEXT_PLACEHOLDER,
        classes=TRIPLE_TEXT_INPUT_P_CLASS,
        style=TRIPLE_TEXT_INPUT_P_STYLE,
    )
    add_connection_text_3 = jp.Input(
        a=add_connection_text_div,
        placeholder= ADD_CONNECTION_TEXT_PLACEHOLDER,
        classes=TRIPLE_TEXT_INPUT_P_CLASS,
        style=TRIPLE_TEXT_INPUT_P_STYLE,
    )
    add_connection_button = jp.Input(
        a=actions_div,
        value="Add Connection",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    def add_connection_button_click(add_connection_text_1: jp.Input, add_connection_text_2: jp.Input, add_connection_text_3: jp.Input, gui: Gui, component, msg):
        text_1, text_2, text_3 = add_connection_text_1.value, add_connection_text_2.value, add_connection_text_3.value
        gui.logger.info("Clicked add_connection: " + text_1 + text_2 + text_3 + f"with mode: {gui.mode}")
        graph = gui.graph
        defined_locations = len(graph)
        try:
            value_1 = int(text_1)
            if value_1 > 0:
                if value_1 > defined_locations:
                    add_connection_text_1.value = f"Err: > {defined_locations}"
                    return
            else:
                add_connection_text_1.value = "Err: < 0"
                return
        except ValueError:
            add_connection_text_1.value = "Err: NAN"
            return
        try:
            value_2 = int(text_2)
            if value_2 > 0:
                if value_2 > defined_locations:
                    add_connection_text_2.value = f"Err: > {defined_locations}"
                    return
            else:
                add_connection_text_2.value = "Err: < 0"
                return
        except ValueError:
            add_connection_text_2.value = "Err: NAN"
            return
        try:
            value_3 = int(text_3)
            if value_3 < 0:
                add_connection_text_3.value = "Err: < 0"
                return
        except ValueError:
            add_connection_text_3.value = "Err: NAN"
            return

        if gui.mode == Mode.GENERATING_PROBLEM:
            gui.graph.add_edge(f"L_{value_1}", f"L_{value_2}", weight=value_3)
            gui.display_graph(True)
            add_connection_text_1.value = ADD_CONNECTION_TEXT_PLACEHOLDER
            add_connection_text_2.value = ADD_CONNECTION_TEXT_PLACEHOLDER
            add_connection_text_3.value = ADD_CONNECTION_TEXT_PLACEHOLDER
    add_connection_button.on('click', partial(add_connection_button_click, add_connection_text_1, add_connection_text_2, add_connection_text_3, gui))

    # Remove Connection
    REMOVE_CONNECTION_TEXT_PLACEHOLDER = ""
    remove_connection_text_div = jp.Div(
        a=actions_div,
        classes=DOUBLE_SLOT_DIV_CLASS, # TODO change
        style=DOUBLE_SLOT_DIV_STYLE,
    )
    remove_connection_text_1 = jp.Input(
        a=remove_connection_text_div,
        placeholder= REMOVE_CONNECTION_TEXT_PLACEHOLDER,
        classes=DOUBLE_TEXT_INPUT_P_CLASS,
        style=DOUBLE_TEXT_INPUT_P_STYLE,
    )
    remove_connection_text_2 = jp.Input(
        a=remove_connection_text_div,
        placeholder= REMOVE_CONNECTION_TEXT_PLACEHOLDER,
        classes=DOUBLE_TEXT_INPUT_P_CLASS,
        style=DOUBLE_TEXT_INPUT_P_STYLE,
    )
    remove_connection_button = jp.Input(
        a=actions_div,
        value="Remove Connection",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    def remove_connection_button_click(remove_connection_text_1: jp.Input, remove_connection_text_2: jp.Input, gui: Gui, component, msg):
        text_1, text_2 = remove_connection_text_1.value, remove_connection_text_2.value
        gui.logger.info("Clicked remove_connection: " + text_1 + text_2 + f"with mode: {gui.mode}")
        graph = gui.graph
        defined_locations = len(graph)
        try:
            value_1 = int(text_1)
            if value_1 > 0:
                if value_1 > defined_locations:
                    remove_connection_text_1.value = f"Err: > {defined_locations}"
                    return
            else:
                remove_connection_text_1.value = "Err: < 0"
                return
        except ValueError:
            remove_connection_text_1.value = "Err: NAN"
            return
        try:
            value_2 = int(text_2)
            if value_2 > 0:
                if value_2 > defined_locations:
                    remove_connection_text_2.value = f"Err: > {defined_locations}"
                    return
            else:
                remove_connection_text_2.value = "Err: < 0"
                return
        except ValueError:
            remove_connection_text_2.value = "Err: NAN"
            return

        if gui.mode == Mode.GENERATING_PROBLEM:
            gui.graph.remove_edge(f"L_{value_1}", f"L_{value_2}")
            gui.display_graph(True)
            remove_connection_text_1.value = REMOVE_CONNECTION_TEXT_PLACEHOLDER
            remove_connection_text_2.value = REMOVE_CONNECTION_TEXT_PLACEHOLDER
    remove_connection_button.on('click', partial(remove_connection_button_click, remove_connection_text_1, remove_connection_text_2, gui))

    # Set Start
    SET_START_TEXT_PLACEHOLDER = ""
    set_start_text = jp.Input(
        a=actions_div,
        placeholder=SET_START_TEXT_PLACEHOLDER,
        classes=TEXT_INPUT_P_CLASS,
        style=TEXT_INPUT_P_STYLE,
    )
    set_start_button = jp.Input(
        a=actions_div,
        value="Set Start",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )

    def set_start_button_click(set_start_text: jp.Input, gui: Gui, component, msg):
        text = set_start_text.value
        gui.logger.info("Clicked set_start: " + text + f" with mode: {gui.mode}")
        try:
            graph = gui.graph
            defined_locations = len(graph)
            value = int(text)
            if value > 0:
                if value <= defined_locations:
                    set_start_text.value = SET_START_TEXT_PLACEHOLDER
                    if gui.mode == Mode.GENERATING_PROBLEM:
                        gui.start = f"L_{value}"
                        gui.display_graph(True)
                else:
                    set_start_text.value = f"Err: > {defined_locations}"
            else:
                set_start_text.value = "Err: <= 0"
        except ValueError:
            set_start_text.value = "Err: NAN"

    set_start_button.on('click', partial(set_start_button_click, set_start_text, gui))

    # Set Destination
    SET_DESTINATION_TEXT_PLACEHOLDER = ""
    set_destination_text = jp.Input(
        a=actions_div,
        placeholder=SET_DESTINATION_TEXT_PLACEHOLDER,
        classes=TEXT_INPUT_P_CLASS,
        style=TEXT_INPUT_P_STYLE,
    )
    set_destination_button = jp.Input(
        a=actions_div,
        value="Set Destination",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )

    def set_destination_button_click(set_destination_text: jp.Input, gui: Gui, component, msg):
        text = set_destination_text.value
        gui.logger.info("Clicked set_destination: " + text + f" with mode: {gui.mode}")
        try:
            graph = gui.graph
            defined_locations = len(graph)
            value = int(text)
            if value > 0:
                if value <= defined_locations:
                    set_destination_text.value = SET_DESTINATION_TEXT_PLACEHOLDER
                    if gui.mode == Mode.GENERATING_PROBLEM:
                        gui.destination = f"L_{value}"
                        gui.display_graph(True)
                else:
                    set_destination_text.value = f"Err: > {defined_locations}"
            else:
                set_destination_text.value = "Err: < 0"
        except ValueError:
            set_destination_text.value = "Err: NAN"

    set_destination_button.on('click', partial(set_destination_button_click, set_destination_text, gui))

    # Randomize Graph
    RANDOMIZE_TEXT_PLACEHOLDER = ""
    randomize_text_div = jp.Div(
        a=actions_div,
        classes=QUADRUPLE_SLOT_DIV_CLASS,
        style=QUADRUPLE_SLOT_DIV_STYLE,
    )
    randomize_text_1 = jp.Input(
        a=randomize_text_div,
        placeholder= RANDOMIZE_TEXT_PLACEHOLDER,
        classes=QUADRUPLE_TEXT_INPUT_P_CLASS,
        style=QUADRUPLE_TEXT_INPUT_P_STYLE,
    )
    randomize_text_2 = jp.Input(
        a=randomize_text_div,
        placeholder= RANDOMIZE_TEXT_PLACEHOLDER,
        classes=QUADRUPLE_TEXT_INPUT_P_CLASS,
        style=QUADRUPLE_TEXT_INPUT_P_STYLE,
    )
    randomize_text_3 = jp.Input(
        a=randomize_text_div,
        placeholder= RANDOMIZE_TEXT_PLACEHOLDER,
        classes=QUADRUPLE_TEXT_INPUT_P_CLASS,
        style=QUADRUPLE_TEXT_INPUT_P_STYLE,
    )
    randomize_text_4 = jp.Input(
        a=randomize_text_div,
        placeholder= RANDOMIZE_TEXT_PLACEHOLDER,
        classes=QUADRUPLE_TEXT_INPUT_P_CLASS,
        style=QUADRUPLE_TEXT_INPUT_P_STYLE,
    )
    randomize_button = jp.Input(
        a=actions_div,
        value="Randomize Graph",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    def randomize_button_click(randomize_text_1: jp.Input, randomize_text_2: jp.Input, randomize_text_3: jp.Input, randomize_text_4: jp.Input, gui: Gui, component, msg):
        text_1, text_2 = randomize_text_1.value, randomize_text_2.value
        text_3, text_4 = randomize_text_3.value, randomize_text_4.value
        gui.logger.info("Clicked randomize: " + text_1 + text_2 + f"with mode: {gui.mode}")
        try:
            value_1 = int(text_1)
            if value_1 <= 0:
                randomize_text_1.value = "Err: <= 0"
                return
        except ValueError:
            randomize_text_1.value = "Err: NAN"
            return
        try:
            value_2 = int(text_2)
            if value_2 <= 0:
                randomize_text_2.value = "Err: <= 0"
                return
        except ValueError:
            randomize_text_2.value = "Err: NAN"
            return
        try:
            value_3 = int(text_3)
            if value_3 <= 0:
                randomize_text_3.value = "Err: <= 0"
                return
        except ValueError:
            randomize_text_3.value = "Err: NAN"
            return
        try:
            value_4 = int(text_4)
            if value_4 <= 0:
                randomize_text_4.value = "Err: <= 0"
                return
        except ValueError:
            randomize_text_4.value = "Err: NAN"
            return
        gui.randomize_graph_click(value_1, value_2, value_3, value_4)
    randomize_button.on('click', partial(randomize_button_click, randomize_text_1, randomize_text_2, randomize_text_3, randomize_text_4, gui))

    reset = jp.Input(
        a=actions_div,
        value="RESET",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    reset.on('click', gui.clear_activities_click)
    solve = jp.Input(
        a=actions_div,
        value="NAVIGATE",
        type="submit",
        classes=ADD_BUTTON_CLASS,
        style=ADD_BUTTON_STYLE,
    )
    solve.on('click', gui.generate_problem_click)

    goals_div = jp.Div(
        a=main_body_div,
        text="GRAPH:",
        classes=GOALS_DIV_CLASS,
        style=GOALS_DIV_STYLE,
    )

    graph_image_div = jp.Div(
        a=goals_div,
        classes="",
        style="",
    )
    gui.graph_image_div = graph_image_div

    gui.display_graph()

    plan_div = jp.Div(
        a=main_body_div,
        text="PLAN:",
        classes=PLAN_DIV_CLASS,
        style=PLAN_DIV_STYLE,
    )
    gui.plan_div = plan_div

    gui.update_planning_execution()

    return wp
