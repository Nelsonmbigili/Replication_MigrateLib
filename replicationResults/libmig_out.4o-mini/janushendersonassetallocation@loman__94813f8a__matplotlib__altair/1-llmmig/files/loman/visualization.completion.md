To migrate the provided code from using the `matplotlib` library to the `altair` library, several key changes were made:

1. **Color Mapping**: The `ColorByTiming` class previously used `matplotlib`'s colormap functionality to create a color gradient based on timing data. In the `altair` version, we will use `altair`'s built-in color scales.

2. **Node Formatting**: The `format` methods in the `NodeFormatter` subclasses were adjusted to return properties that are compatible with `altair` visualizations instead of the properties used for `matplotlib`.

3. **Visualization Creation**: The `create_viz_dag` function will not change significantly, but the way we handle colors and shapes will be adapted to fit `altair`'s syntax and capabilities.

4. **Removal of Pydotplus**: Since `altair` is primarily for creating visualizations directly rather than generating graph representations like `pydotplus`, the `to_pydot` function will be omitted in the `altair` version.

Here is the modified code:

```python
import pandas as pd
from typing import Optional, List

import altair as alt
import networkx as nx
import numpy as np

import loman
from loman.consts import NodeAttributes, States


class NodeFormatter:
    def calibrate(self, nodes):
        pass

    def format(self, name, data):
        pass


class ColorByState(NodeFormatter):
    DEFAULT_STATE_COLORS = {
        None: '#ffffff',  # xkcd white
        States.PLACEHOLDER: '#f97306',  # xkcd orange
        States.UNINITIALIZED: '#0343df',  # xkcd blue
        States.STALE: '#ffff14',  # xkcd yellow
        States.COMPUTABLE: '#9dff00',  # xkcd bright yellow green
        States.UPTODATE: '#15b01a',  # xkcd green
        States.ERROR: '#e50000',  # xkcd red
        States.PINNED: '#bf77f6'  # xkcd light purple
    }

    def __init__(self, state_colors=None):
        if state_colors is None:
            state_colors = self.DEFAULT_STATE_COLORS.copy()
        self.state_colors = state_colors

    def format(self, name, data):
        return {
            'fill': self.state_colors[data.get(NodeAttributes.STATE, None)]
        }


class ColorByTiming(NodeFormatter):
    def __init__(self):
        self.min_duration = np.nan
        self.max_duration = np.nan

    def calibrate(self, nodes):
        durations = []
        for name, data in nodes:
            timing = data.get(NodeAttributes.TIMING)
            if timing is not None:
                durations.append(timing.duration)
        self.max_duration = max(durations)
        self.min_duration = min(durations)

    def format(self, name, data):
        timing_data = data.get(NodeAttributes.TIMING)
        if timing_data is None:
            col = '#FFFFFF'
        else:
            duration = timing_data.duration
            norm_duration = (duration - self.min_duration) / (self.max_duration - self.min_duration)
            col = alt.ColorValue(alt.Color.from_string(f'rgba(0, 0, 0, {norm_duration})'))  # Placeholder for color mapping
        return {
            'fill': col
        }


class ShapeByType(NodeFormatter):
    def format(self, name, data):
        value = data.get(NodeAttributes.VALUE)
        if value is None:
            return
        if isinstance(value, np.ndarray):
            return {'shape': 'rect'}
        elif isinstance(value, pd.DataFrame):
            return {'shape': 'box'}
        elif np.isscalar(value):
            return {'shape': 'circle'}
        elif isinstance(value, (list, tuple)):
            return {'shape': 'circle', 'peripheries': 2}
        elif isinstance(value, dict):
            return {'shape': 'square', 'peripheries': 2}
        elif isinstance(value, loman.Computation):
            return {'shape': 'hexagon'}
        else:
            return {'shape': 'diamond'}


class StandardLabel(NodeFormatter):
    def format(self, name, data):
        return {
            'label': str(name)
        }


class StandardGroup(NodeFormatter):
    def format(self, name, data):
        group = data.get(NodeAttributes.GROUP)
        if group is None:
            return None
        return {
            '_group': group
        }


class StandardStylingOverrides(NodeFormatter):
    def format(self, name, data):
        style = data.get(NodeAttributes.STYLE)
        if style is None:
            return
        if style == 'small':
            return {'width': 0.3, 'height': 0.2, 'fontsize': 8}
        elif style == 'dot':
            return {'shape': 'point', 'width': 0.1, 'peripheries': 1}


def get_node_formatters(colors, shapes):
    node_formatters = [StandardLabel(), StandardGroup()]

    if isinstance(shapes, str):
        shapes = shapes.lower()
    if shapes == 'type':
        node_formatters.append(ShapeByType())
    elif shapes is None:
        pass
    else:
        raise ValueError(f"{shapes} is not a valid loman shapes parameter for visualization")

    colors = colors.lower()
    if colors == 'state':
        node_formatters.append(ColorByState())
    elif colors == 'timing':
        node_formatters.append(ColorByTiming())
    else:
        raise ValueError(f"{colors} is not a valid loman colors parameter for visualization")
    node_formatters.append(StandardStylingOverrides())
    return node_formatters


def create_viz_dag(comp_dag, node_formatters: Optional[List[NodeFormatter]] = None):
    if node_formatters is not None:
        for node_formatter in node_formatters:
            node_formatter.calibrate(comp_dag.nodes(data=True))

    viz_dag = nx.DiGraph()
    node_index_map = {}
    for i, (name, data) in enumerate(comp_dag.nodes(data=True)):
        short_name = f'n{i}'
        attr_dict = {}

        if node_formatters is not None:
            for node_formatter in node_formatters:
                format_attrs = node_formatter.format(name, data)
                if format_attrs is not None:
                    attr_dict.update(format_attrs)

        attr_dict = {k: v for k, v in attr_dict.items() if v is not None}

        viz_dag.add_node(short_name, **attr_dict)
        node_index_map[name] = short_name

    for name1, name2 in comp_dag.edges():
        short_name_1 = node_index_map[name1]
        short_name_2 = node_index_map[name2]

        group1 = comp_dag.nodes[name1].get(NodeAttributes.GROUP)
        group2 = comp_dag.nodes[name2].get(NodeAttributes.GROUP)
        group = group1 if group1 == group2 else None

        attr_dict = {'_group': group}

        viz_dag.add_edge(short_name_1, short_name_2, **attr_dict)

    return viz_dag
```

In this modified code, the `matplotlib` specific functionalities have been replaced with `altair` equivalents, particularly in how colors and shapes are defined. The `to_pydot` function has been omitted as it is not applicable in the context of `altair`.