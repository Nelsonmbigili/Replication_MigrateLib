### Explanation of Changes

To migrate the provided code from using the `seaborn` library to the `plotly` library, I made the following changes:

1. **Import Statements**: I replaced the import of `seaborn` with `plotly.express` and removed the import of `matplotlib.pyplot` since `plotly` handles plotting differently.
  
2. **Clustermap**: The `sns.clustermap` function was replaced with `plotly.express.imshow`, which is used to display a heatmap of the similarity matrix.

3. **Violin Plot**: The `sns.violinplot` function was replaced with `plotly.express.violin`, which creates a violin plot in a similar manner.

4. **Linear Model Plot**: The `sns.lmplot` function was replaced with `plotly.express.scatter`, which allows for scatter plots with a trendline. The trendline is specified using the `trendline` parameter.

5. **Line Plot**: The `sns.lineplot` function was replaced with `plotly.express.line`, which creates a line plot. The legend handling is done differently in `plotly`.

6. **Layout Adjustments**: Adjustments for layout and axis labels are handled differently in `plotly`, so I removed the `plt.tight_layout()` calls and adjusted the axis labels directly in the `plotly` functions.

Here is the modified code:

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
    :return: a heatmap figure

    Example:

    >>> from cdlib import algorithms, viz, evaluation
    >>> import networkx as nx
    >>> g = nx.karate_club_graph()
    >>> coms = algorithms.louvain(g)
    >>> coms2 = algorithms.walktrap(g)
    >>> heatmap = viz.plot_sim_matrix([coms,coms2],evaluation.adjusted_mutual_information)

    """
    forDF = []
    for c in clusterings:
        cID = c.get_description()
        for c2 in clusterings:
            c2ID = c2.get_description()
            forDF.append([cID, c2ID, scoring(c, c2).score])
    df = pd.DataFrame(columns=["com1", "com2", "score"], data=forDF)
    df = df.pivot(index="com1", columns="com2", values="score")
    fig = px.imshow(df, labels=dict(x="com2", y="com1", color="score"), color_continuous_scale='Viridis')
    return fig


def plot_com_stat(
    com_clusters: list, com_fitness: Callable[[object, object, bool], object]
) -> object:
    """
    Plot the distribution of a property among all communities for a clustering, or a list of clusterings (violin-plots)

    :param com_clusters: list of clusterings to compare, or a single clustering
    :param com_fitness: the fitness/community property to use
    :return: the violin-plots

    Example:

    >>> from cdlib import algorithms, viz, evaluation
    >>> import networkx as nx
    >>> g = nx.karate_club_graph()
    >>> coms = algorithms.louvain(g)
    >>> coms2 = algorithms.walktrap(g)
    >>> violinplot = viz.plot_com_stat([coms,coms2],evaluation.size)

    """
    if isinstance(com_clusters, cdlib.classes.clustering.Clustering):
        com_clusters = [com_clusters]

    allVals = []
    allNames = []
    for c in com_clusters:
        prop = com_fitness(c.graph, c, summary=False)
        allVals += prop
        allNames += [c.get_description()] * len(prop)

    df = pd.DataFrame({"Algorithm": allNames, "Value": allVals})
    fig = px.violin(df, y="Value", x="Algorithm", box=True, points="all", color="Algorithm")
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
    :param kwargs: parameters for the plotly scatter
    :return: a plotly scatter plot

    Example:

    >>> from cdlib import algorithms, viz, evaluation
    >>> import networkx as nx
    >>> g = nx.karate_club_graph()
    >>> coms = algorithms.louvain(g)
    >>> coms2 = algorithms.walktrap(g)
    >>> scatter = viz.plot_com_properties_relation([coms,coms2],evaluation.size,evaluation.internal_edge_density)
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
    fig = px.scatter(df, x=com_fitness_x.__name__, y=com_fitness_y.__name__, color="Method", trendline="ols", **kwargs)
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
    :return: a plotly line plot

    Example:

    >>> from cdlib import algorithms, viz, evaluation
    >>> import networkx as nx
    >>> g1 = nx.algorithms.community.LFR_benchmark_graph(1000, 3, 1.5, 0.5, min_community=20, average_degree=5)
    >>> g2 = nx.algorithms.community.LFR_benchmark_graph(1000, 3, 1.5, 0.7, min_community=20, average_degree=5)
    >>> names = ["g1", "g2"]
    >>> graphs = [g1, g2]
    >>> for g in graphs:
    >>>     references.append(NodeClustering(communities={frozenset(g.nodes[v]['community']) for v in g}, graph=g, method_name="reference"))
    >>> algos = [algorithms.crisp_partition.louvain, algorithms.crisp_partition.label_propagation]
    >>> viz.plot_scoring(graphs, references, names, algos, nbRuns=2)

    """
    forDF = []
    for i, g in enumerate(graphs):
        for m in methods:
            for r in range(nbRuns):
                partition = m(g)

                score = scoring(partition, ref_partitions[i]).score
                forDF.append([graph_names[i], score, partition.get_description()])
    df = pd.DataFrame(columns=["graph", "score", "method"], data=forDF)
    fig = px.line(df, x="graph", y="score", color="method", markers=True)
    return fig
``` 

This modified code now uses `plotly` for all visualizations, maintaining the original functionality while adapting to the new library's syntax and capabilities.