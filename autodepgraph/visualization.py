import networkx as nx
import numpy as np
from autodepgraph.pg_visualization.pg_remotegraph import pg_DiGraph_window

# Colormap used to map states to node colors
state_cmap = {'unknown': '#7f7f7f',            # middle gray
              'active': '#1f77b4',             # muted blue
              'good': '#2ca02c',               # cooked asparagus green
              'needs calibration': '#ff7f0e',  # safety orange
              'bad': '#d62728',                # brick red
              }

type_symbol_map = {'normal': 'o',              # a circle
                   'manual_cal': 'h', }        # a hexagon


def get_state_col_map(snapshot):
    """
    Creates a dictionary with node names as keys and their state dependent
    color as value.
    """
    col_map = {}
    for node in snapshot['nodes'].values():
        col_map[node['name']] = \
            state_cmap[node['parameters']['state']['value']]

    return col_map


def get_type_symbol_map(snapshot):
    """
    Returns a dictionary with node names as keys and a type dependent symbol
    as value.

    Currently there is only a distinction between "normal" nodes and
    "manual_cal" nodes. "manual_cal" nodes are those nodes that do not have
    a calibrate function specified and as such need to be set by hand.
    Normal nodes are all other nodes.
    """
    symb_map = {}
    for node in snapshot['nodes'].values():
        if (node['parameters']['calibrate_function']['value']
                == 'NotImplementedCalibration'):
            state = 'manual_cal'
        else:
            state = 'normal'
        symb_map[node['name']] = \
            type_symbol_map[state]
    return symb_map


def snapshot_to_nxGraph(snapshot):
    """
    Creates a networkx graph object from a snapshot of a graph.
    This is mostly used for determining positions of the nodes required for
    plotting.
    """
    g_snap = snapshot['nodes']
    nxG = nx.DiGraph()
    nxG.add_nodes_from(g_snap)
    for node_name, n_snap in g_snap.items():
        for dependency in n_snap['parameters']['parents']['value']:
            nxG.add_edge(node_name, dependency)
    return nxG


def draw_graph_mpl(snapshot, pos=None):
    """
    Function to create a quick plot of a graph using matplotlib.
    Intended mostly for for debugging purposes
    Args:
        snapshot    snapshot snapshot of the graph
        pos         positions of the nodes
    returns:
        pos

    """
    nxG = snapshot_to_nxGraph(snapshot)
    if pos is None:
        pos = nx.spring_layout(nxG, iterations=5000)

    # Edge colors need to be set using a value mapping and a cmap

    cm = get_state_col_map(snapshot)
    colors_list = [cm[node] for node in nxG.nodes()]

    nx.draw_networkx_nodes(nxG, pos, node_color=colors_list)
    # Arrows look pretty bad
    nx.draw_networkx_edges(nxG, pos, arrows=True)
    nx.draw_networkx_labels(nxG, pos)
    return pos


def adjaceny_to_integers(nxG, pos_dict):
    """
    Helper function that takes a networkx graph object and returns the
    edges (adjacency) as an array of integers.

    Args:
        nxG : networkx graph object, contains the defined edges
        pos_dict : dictionary from the layout, contains the relevant order
            of the nodes
    returns:
        adj : array of integers specifying the edges
    """

    node_name_list = list(pos_dict.keys())
    adj = []
    for child, parent in nxG.edges():
        child_idx = node_name_list.index(child)
        parent_idx = node_name_list.index(parent)
        adj.append([child_idx, parent_idx])
    adj = np.array(adj)
    return adj


def draw_graph_pyqt(snapshot, DiGraphWindow=None, window_title=None):
    """
    Function to create a quick plot of a graph using matplotlib.
    Intended mostly for for debugging purposes
    Args:
        snapshot        : snapshot of the graph
        DiGraphWindow   : pyqtgraph remote graph window to be updated
            if None it will create a new plotting window to update
        window_title    : title of the plotting window
    returns:
        DiGraphWindow

    """
    nxG = snapshot_to_nxGraph(snapshot)

    # Converts it to an array to work with pyqtgraph plotting class
    pos_dict = nx.nx_agraph.graphviz_layout(nxG, prog='dot')
    pos = np.array(list(pos_dict.values()))
    adj = adjaceny_to_integers(nxG, pos_dict)

    # Edge colors need to be set using a value mapping and a cmap
    cm = get_state_col_map(snapshot)
    colors_list = [(cm[node]) for node in pos_dict.keys()]

    sm = get_type_symbol_map(snapshot)
    symbols = [(sm[node]) for node in pos_dict.keys()]

    labels = list(pos_dict.keys())

    if DiGraphWindow is None:
        DiGraphWindow = pg_DiGraph_window(window_title=window_title)

    DiGraphWindow.setData(pos=np.array(pos), adj=adj, size=20, symbol=symbols,
                          labels=labels, pen=(60, 60, 60),
                          symbolBrush=colors_list, pxMode=False)
    return DiGraphWindow
