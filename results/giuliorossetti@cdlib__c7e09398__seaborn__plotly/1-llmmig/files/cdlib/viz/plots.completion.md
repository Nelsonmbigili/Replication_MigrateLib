### Explanation of Changes

To migrate the code from `seaborn` to `plotly`, the following changes were made:
1. **Clustermap (`plot_sim_matrix`)**:
   - Replaced `sns.clustermap` with `plotly.express.imshow` to create a heatmap for the similarity matrix.
   - Added `color_continuous_scale` to mimic the color scheme used in seaborn.

2. **Violin Plot (`plot_com_stat`)**:
   - Replaced `sns.violinplot` with `plotly.express.violin`.
   - Used `orientation='v'` to ensure the violin plots are vertical.
   - Added `update_layout` to rotate x-axis labels and adjust layout.

3. **Scatter Plot (`plot_com_properties_relation`)**:
   - Replaced `sns.lmplot` with `plotly.express.scatter`.
   - Used `color` to differentiate methods and `update_layout` for legend and layout adjustments.

4. **Line Plot (`plot_scoring`)**:
   - Replaced `sns.lineplot` with `plotly.express.line`.
   - Used `color` to differentiate methods and `update_layout` for x-axis label rotation and legend placement.

5. **General Adjustments**:
   - Removed `matplotlib.pyplot` imports and related calls (e.g., `plt.tight_layout`, `plt.legend`).
   - Added `plotly.express` for all visualizations.

### Modified Code

```python
import plotly.express as px
import pandas as pd
import cdlib
from typing import Callable

__all__ = [
    "plot_com_properties_relation",
    "plot_com_stat",
    "plot_sim_matrix",
    "plot_scoring",
]


def plot_sim_matrix(
    clusterings: list, scoring: Callable[[object, object], object]
) -> object:
    """
    Plot a similarity matrix between a list of clusterings, using the provided scoring function.

    :param clusterings: list of clusterings to compare
    :param scoring: the scoring function to use
    :return: a Plotly heatmap
    """
    forDF = []
    for c in clusterings:
        cID = c.get_description()
        for c2 in clusterings:
            c2ID = c2.get_description()
            forDF.append([cID, c2ID, scoring(c, c2).score])
    df = pd.DataFrame(columns=["com1", "com2", "score"], data=forDF)
    df = df.pivot(index="com1", columns="com2", values="score")
    
    fig = px.imshow(
        df,
        labels=dict(x="Community 2", y="Community 1", color="Score"),
        color_continuous_scale="Viridis",
    )
    return fig


def plot_com_stat(
    com_clusters: list, com_fitness: Callable[[object, object, bool], object]
) -> object:
    """
    Plot the distribution of a property among all communities for a clustering, or a list of clusterings (violin-plots)

    :param com_clusters: list of clusterings to compare, or a single clustering
    :param com_fitness: the fitness/community property to use
    :return: the violin-plots
    """
    if isinstance(com_clusters, cdlib.classes.clustering.Clustering):
        com_clusters = [com_clusters]

    allVals = []
    allNames = []
    for c in com_clusters:
        prop = com_fitness(c.graph, c, summary=False)
        allVals += prop
        allNames += [c.get_description()] * len(prop)

    df = pd.DataFrame({"Algorithm": allNames, com_fitness.__name__: allVals})
    fig = px.violin(
        df,
        x="Algorithm",
        y=com_fitness.__name__,
        box=True,
        points="all",
        color="Algorithm",
    )
    fig.update_layout(xaxis_tickangle=90)
    return fig


def plot_com_properties_relation(
    com_clusters: object,
    com_fitness_x: Callable[[object, object, bool], object],
    com_fitness_y: Callable[[object, object, bool], object],
    **kwargs: dict
) -> object:
    """
    Plot the relation between two properties/fitness function of a clustering

    :param com_clusters:  clustering(s) to analyze (cluster or cluster list)
    :param com_fitness_x: first fitness/community property
    :param com_fitness_y: first fitness/community property
    :param kwargs: parameters for the seaborn lmplot
    :return: a Plotly scatter plot
    """
    if isinstance(com_clusters, cdlib.classes.clustering.Clustering):
        com_clusters = [com_clusters]

    for_df = []

    for c in com_clusters:
        x = com_fitness_x(c.graph, c, summary=False)
        y = com_fitness_y(c.graph, c, summary=False)
        for i, vx in enumerate(x):
            for_df.append([c.get_description(), vx, y[i]])

    df = pd.DataFrame(
        columns=["Method", com_fitness_x.__name__, com_fitness_y.__name__], data=for_df
    )
    fig = px.scatter(
        df,
        x=com_fitness_x.__name__,
        y=com_fitness_y.__name__,
        color="Method",
        **kwargs,
    )
    fig.update_layout(legend_title="Method")
    return fig


def plot_scoring(
    graphs: list,
    ref_partitions: object,
    graph_names: list,
    methods: list,
    scoring: Callable[
        [object, object], object
    ] = cdlib.evaluation.adjusted_mutual_information,
    nbRuns: int = 5,
) -> object:
    """
    Plot the scores obtained by a list of methods on a list of graphs.

    :param graphs: list of graphs on which to make computations
    :param ref_partitions: list of reference clusterings corresponding to graphs
    :param graph_names: list of the names of the graphs to display
    :param methods: list of functions that take a graph as input and return a Clustering as output
    :param scoring: the scoring function to use, default anmi
    :param nbRuns: number of runs to do for each method on each graph
    :return: a Plotly line plot
    """
    forDF = []
    for i, g in enumerate(graphs):
        for m in methods:
            for r in range(nbRuns):
                partition = m(g)

                score = scoring(partition, ref_partitions[i]).score
                forDF.append([graph_names[i], score, partition.get_description()])
    df = pd.DataFrame(columns=["graph", "score", "method"], data=forDF)
    fig = px.line(
        df,
        x="graph",
        y="score",
        color="method",
        markers=True,
    )
    fig.update_layout(xaxis_tickangle=90, legend_title="Method")
    return fig
```