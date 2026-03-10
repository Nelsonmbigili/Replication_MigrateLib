"""Helper functions for constructing visualizations."""

import itertools
import math
from typing import Dict, List, Union

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from IPython.core.interactiveshell import InteractiveShell
from sklearn.metrics import confusion_matrix
from wordcloud import WordCloud

import tx2.wrapper
from tx2 import calc, utils, STOPWORDS


# if foreground_color is None, it will automatically decide white or black by color
def get_nice_html_label(text: str, color: str, foreground_color: str = None) -> str:
    """Get a nice looking colored background label.

    :param text: The text to display in the label.
    :param color: The background color as a hex string ('#XXXXXX') for the label
    :param foreground_color: Leave as None for an automatic black/white foreground color
        determination from :meth:`contrasting_text_color`.
    :return: An HTML string for the label.
    """
    # determine if foreground should be white or black
    if foreground_color is None:
        foreground_color = contrasting_text_color(color)

    label = f"<span style='background-color: {color}; color: {foreground_color}; padding: 3px; border-radius: 5px;'>{text}</span>"
    return label


# https://stackoverflow.com/questions/1855884/determine-font-color-based-on-background-color
def contrasting_text_color(hex_str: str) -> str:
    """Get a contrasting foreground text color for specified background hex color

    :param hext_str: A hex string color ('#XXXXXX') for which to determine a black-or-white
        foreground color.
    :return: '#FFF' or '#000'.
    """
    r, g, b = (hex_str[1:3], hex_str[3:5], hex_str[5:])

    luminance = (int(r, 16) * 0.299 + int(g, 16) * 0.587 + int(b, 16) * 0.114) / 255

    if luminance > 0.5:
        return "#000"
    else:
        return "#FFF"


def render_html_text(text, transformer_wrapper: tx2.wrapper.Wrapper) -> str:
    """Get a text-salience highlighted HTML paragraph.

    :param text: The text to run salience on and render.
    :param transformer_wrapper: The :class:`tx2.wrapper.Wrapper` instance.
    :return: An HTML string with span-styled-highlights on each relevant word.
    """
    deltas = calc.salience_map(
        transformer_wrapper.soft_classify, text[:512], transformer_wrapper.encodings
    )
    normalised_d = calc.normalize_salience_map(deltas)

    html = "<p>"
    for word in text.split(" "):
        if word in normalised_d:
            html += f"<span style='background-color: rgba(255, 100, 0.0, {normalised_d[word]});'>{word}</span> "
        else:
            html += word + " "
    html += "<p>"
    return html


_cached_wordclouds = {}


def prepare_wordclouds(
    clusters: Dict[str, List[int]], test_texts: Union[np.ndarray, pd.Series]
):
    """Pre-render the wordcloud for each cluster, this makes switching the main wordcloud figure faster.

    :param clusters: Dictionary of clusters where the values are the lists of dataframe indices for the entries in each cluster.
    :param test_texts: The full test corpus.
    """
    for cluster in clusters:
        _cached_wordclouds[cluster] = gen_wordcloud(test_texts[clusters[cluster]])


def gen_wordcloud(texts: Union[np.ndarray, pd.Series]):
    """Creates and returns a wordcloud image that can be rendered with :code:`plt.imshow`.

    :param texts: Collection of strings to get text statistics from.
    :return: The generated wordcloud image.
    """
    text = " ".join(list(texts))
    cloud = WordCloud(
        stopwords=set(STOPWORDS), background_color="white", width=800, height=400
    ).generate(text)
    return cloud


def plot_big_wordcloud(index: int, clusters: Dict[str, List[int]]):
    """Render the word cloud that the currently selected point is in.

    :param index: The index of the point to find the cluster of.
    :param clusters: The dictionary of clusters where the values are the lists of indices of entries in that cluster.
    """
    cluster = utils.which_cluster(index, clusters)
    fig = go.Figure()
    fig.add_trace(go.Image(z=_cached_wordclouds[cluster]))
    fig.update_layout(title=str(cluster), margin=dict(l=0, r=0, t=30, b=0))
    return fig


def plot_passed_wordcloud(cloud, name):
    """Render the given word cloud.

    :param cloud: The word cloud to render.
    :param name: The title to render with the word cloud.
    """
    fig = go.Figure()
    fig.add_trace(go.Image(z=cloud))
    fig.update_layout(title=name, margin=dict(l=0, r=0, t=30, b=0))
    return fig


def plot_wordclouds(dashboard):
    """Render the grid of all wordclouds.

    :param dashboard: The current dashboard, needed in order to grab the cluster data.
    """
    num_cols = 4
    num_rows = max(math.ceil(len(dashboard.transformer_wrapper.clusters) / num_cols), 2)

    fig = make_subplots(rows=num_rows, cols=num_cols, specs=[[{'type': 'image'}]*num_cols]*num_rows)

    for index, cluster in enumerate(dashboard.transformer_wrapper.clusters):
        ax_x = int(index / num_cols) + 1
        ax_y = index % num_cols + 1
        fig.add_trace(go.Image(z=_cached_wordclouds[cluster]), row=ax_x, col=ax_y)
        fig.update_xaxes(showticklabels=False, row=ax_x, col=ax_y)
        fig.update_yaxes(showticklabels=False, row=ax_x, col=ax_y)
        fig.update_layout(title=str(cluster), margin=dict(l=0, r=0, t=30, b=0))

    return fig


def plot_metrics(pred_y: List[int], target_y: List[int], encodings: Dict[str, int]):
    """Get colored dataframes with macro and micro scores for the given predictions on an aggregate level and per class.

    :param pred_y: Predicted labels.
    :param target_y: Actual labels.
    :param encodings: Dictionary of string label -> numeric label.
    :return: The per-class metrics dataframe and the aggregate metrics dataframe.
    """
    temp_dict = {"pred": pred_y, "target": target_y}
    temp_df = pd.DataFrame.from_dict(temp_dict)
    per_class, macros, micros = calc.prediction_scores(
        temp_df, "target", "pred", encodings
    )

    per_df_rows = []
    for metric in "precision", "recall", "f1":
        row = {"metric": metric}
        for key in per_class:
            row[utils.get_cat_by_index(key, encodings)] = per_class[key][metric]

        per_df_rows.append(row)

    per_df = pd.DataFrame(per_df_rows).style.background_gradient(
        cmap="RdYlGn", vmax=1.0, vmin=0.0
    )

    aggregate_rows = []
    for metric in "precision", "recall", "f1":
        aggregate_rows.append(
            {"metric": metric, "macro": macros[metric], "micro": micros[metric]}
        )

    agg_df = pd.DataFrame(aggregate_rows).style.background_gradient(
        cmap="RdYlGn", vmax=1.0, vmin=0.0
    )

    return per_df, agg_df


def plot_confusion_matrix(
    pred_y: List[int], target_y: List[int], encodings: Dict[str, int], figsize=(8, 8)
):
    """Get the confusion matrix for given predictions.

    :param pred_y: Predicted labels.
    :param target_y: Actual labels.
    :param encodings: Dictionary of string label -> numeric label.
    :param figsize: the size with which to
    """
    labels = []
    encoded = []
    for i in range(len(encodings.keys())):
        for key, value in encodings.items():
            if value == i:
                labels.append(key)
                encoded.append(value)
                break
    cm = confusion_matrix(target_y, pred_y, labels=list(encodings.values()))

    acc = np.trace(cm) / float(np.sum(cm))
    miss = 1 - acc

    fig = go.Figure(data=go.Heatmap(z=cm, x=labels, y=labels, colorscale='Blues'))
    fig.update_layout(title=f"Predicted label\naccuracy={acc:.4f}; misclassified={miss:.4f}",
                      xaxis_title="Predicted label",
                      yaxis_title="True label",
                      margin=dict(l=0, r=0, t=30, b=0))

    text_fg_threshold = cm.max() / 1.5
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        fig.add_annotation(
            x=j,
            y=i,
            text="{:,}".format(cm[i, j]),
            showarrow=False,
            font=dict(color="white" if cm[i, j] > text_fg_threshold else "black"),
            xref="x",
            yref="y"
        )

    return fig


def _get_scatter_points_from_embeddings(
    colors_array,
    embeddings: np.ndarray,
    target_classes: Union[np.ndarray, pd.Series] = None,
):
    """DOES NOT DISPLAY GRAPH, just a helper for splitting out the UMAP embeddings."""

    if len(embeddings) == 0:
        return np.array([]), np.array([]), np.array([])

    if target_classes is None:
        colors = np.array(colors_array[0] * len(embeddings))
    else:
        colors = np.array(
            [colors_array[class_val] for class_val in list(target_classes)]
        )

    x = embeddings[:, 0]
    y = embeddings[:, 1]

    return x, y, colors


@utils.debounce(1.0)
def plot_embedding_projections(text, dashboard, prediction=None):
    dashboard.html_graph_status.value = (
        "<p>" + tx2.visualization.get_nice_html_label("Graphing...", "#FF0000") + "</p>"
    )
    fig = go.Figure()

    # render all test data projections
    if not dashboard.chk_focus_errors.value:
        testing_x, testing_y, testing_c = _get_scatter_points_from_embeddings(
            dashboard.colors,
            np.array(dashboard.transformer_wrapper.projections_testing),
            dashboard.transformer_wrapper.test_labels,
        )
        fig.add_trace(go.Scatter(
            x=testing_x, y=testing_y, mode='markers', marker=dict(color=testing_c, opacity=0.8, size=dashboard.point_size)
        ))
    else:
        # render incorrect test data

        df_temp = pd.DataFrame.from_dict(
            {
                "pred": dashboard.transformer_wrapper.predictions,
                "target": dashboard.transformer_wrapper.test_labels,
            }
        )
        df_incorrect = df_temp[df_temp.pred != df_temp.target]

        incorrect_indices = list(df_incorrect.index)
        incorrect_projections = [
            dashboard.transformer_wrapper.projections_testing[i]
            for i in range(len(dashboard.transformer_wrapper.projections_testing))
            if i in incorrect_indices
        ]
        incorrect_x, incorrect_y, incorrect_c = _get_scatter_points_from_embeddings(
            dashboard.colors, np.array(incorrect_projections), df_incorrect.target
        )
        fig.add_trace(go.Scatter(
            x=incorrect_x,
            y=incorrect_y,
            mode='markers',
            marker=dict(color=incorrect_c, opacity=0.8, size=dashboard.point_size)
        ))
        testing_x, testing_y, testing_c = incorrect_x, incorrect_y, incorrect_c

        # render correct test data
        df_correct = df_temp[df_temp.pred == df_temp.target]
        correct_indices = list(df_correct.index)
        correct_projections = [
            dashboard.transformer_wrapper.projections_testing[i]
            for i in range(len(dashboard.transformer_wrapper.projections_testing))
            if i in correct_indices
        ]
        correct_x, correct_y, correct_c = _get_scatter_points_from_embeddings(
            dashboard.colors, np.array(correct_projections), df_correct.target
        )
        fig.add_trace(go.Scatter(
            x=correct_x,
            y=correct_y,
            mode='markers',
            marker=dict(color=correct_c, opacity=0.1, size=dashboard.unfocused_point_size)
        ))

    # render training data projections
    if dashboard.chk_show_train.value:
        training_x, training_y, training_c = _get_scatter_points_from_embeddings(
            dashboard.colors,
            np.array(dashboard.transformer_wrapper.projections_training),
            dashboard.transformer_wrapper.train_labels,
        )
        fig.add_trace(go.Scatter(
            x=training_x,
            y=training_y,
            mode='markers',
            marker=dict(color=training_c, opacity=0.1, size=dashboard.unfocused_point_size)
        ))

    # render highlighted data points
    if len(dashboard.highlight_indices) > 0:
        fig.add_trace(go.Scatter(
            x=testing_x[dashboard.highlight_indices],
            y=testing_y[dashboard.highlight_indices],
            mode='markers',
            marker=dict(color=testing_c[dashboard.highlight_indices], size=dashboard.highlighted_point_size, line=dict(color='red', width=2))
        ))

    # if text differs from the selected index, render new point
    if (
        dashboard.prior_reference_point is None
        or dashboard.prior_reference_text != text
    ):
        text_projection = dashboard.transformer_wrapper.project([text])[0]
        if prediction is None:
            classification = dashboard.transformer_wrapper.classify([text])[0]
            pred_color = dashboard.colors[classification]
        else:
            pred_color = dashboard.colors[prediction]
        fig.add_trace(go.Scatter(
            x=[text_projection[0]],
            y=[text_projection[1]],
            mode='markers',
            marker=dict(color=pred_color, size=dashboard.highlighted_point_size, line=dict(color='black', width=2))
        ))

    # render the original reference point and arrow if applicable
    if dashboard.prior_reference_point is not None:
        fig.add_trace(go.Scatter(
            x=[dashboard.prior_reference_point[0][0]],
            y=[dashboard.prior_reference_point[0][1]],
            mode='markers',
            marker=dict(color=dashboard.prior_reference_point[1], size=dashboard.highlighted_point_size, line=dict(color='black', width=2))
        ))

        # arrow!
        if dashboard.prior_reference_text != text:
            x_dist = text_projection[0] - dashboard.prior_reference_point[0][0]
            y_dist = text_projection[1] - dashboard.prior_reference_point[0][1]
            fig.add_annotation(
                x=dashboard.prior_reference_point[0][0],
                y=dashboard.prior_reference_point[0][1],
                ax=text_projection[0],
                ay=text_projection[1],
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowcolor='black'
            )

    # show visual cluster labels
    if dashboard.chk_show_cluster_labels.value:
        for x, y, label in dashboard.transformer_wrapper.cluster_labels:
            fig.add_annotation(
                x=float(x),
                y=float(y),
                text=label,
                showarrow=False,
                bgcolor='white',
                opacity=0.5,
                bordercolor='black',
                borderwidth=1,
                borderpad=2
            )

    # display legend
    legend_elements = []
    for i in range(0, len(dashboard.transformer_wrapper.encodings)):
        legend_elements.append(
            dict(
                name=list(dashboard.transformer_wrapper.encodings.keys())[i],
                marker=dict(color=dashboard.colors[i]),
                type='scatter',
                mode='markers',
                showlegend=True
            )
        )

    fig.update_layout(legend=dict(items=legend_elements))

    # output
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))

    # NOTE: we essentially mimic the append_display_data function for an output widget
    # https://github.com/jupyter-widgets/ipywidgets/blob/master/python/ipywidgets/ipywidgets/widgets/widget_output.py#L173
    # this otherwise does not work well in jupyter lab because it handles cell
    # outputs slightly differently than notebook, and you're not supposed to use
    # the context manager in a separate thread (caused because of this method's
    # debounce)
    fmt = InteractiveShell.instance().display_formatter.format
    data, metadata = fmt(fig)
    dashboard.out_projection_scatter.outputs = (
        {"output_type": "display_data", "data": data, "metadata": metadata},
    )

    dashboard.html_graph_status.value = (
        "<p>" + tx2.visualization.get_nice_html_label("Ready!", "#008000") + "</p>"
    )


def plot_clusters(clusters, cluster_values):
    """Plot highest word values for each cluster."""
    num_cols = 4

    num_rows = math.ceil(len(clusters) / num_cols)

    fig = go.Figure()

    for index, cluster in enumerate(clusters):
        ax_x = int(index / num_cols)
        ax_y = index % num_cols

        freq = cluster_values[cluster][:10]
        y = [item[1] for item in freq]
        y_labels = [item[0][:20] for item in freq]
        y_pos = np.arange(len(y_labels))
        y_pos = y_pos * -1

        fig.add_trace(go.Bar(
            y=y_pos,
            x=y,
            orientation='h',
            name=str(cluster),
            text=y_labels,
            hoverinfo='text'
        ))

    fig.update_layout(title="Clusters", margin=dict(l=0, r=0, t=30, b=0))
    return fig


def plot_clusters_stacked(clusters, cluster_words_classified, encodings, colors):
    """Plot highest word values for each cluster, colored according to entry classification"""
    num_cols = 4

    num_rows = math.ceil(len(clusters) / num_cols)

    fig = go.Figure()

    for index, cluster in enumerate(clusters):
        ax_x = int(index / num_cols)
        ax_y = index % num_cols

        words = list(cluster_words_classified[cluster].keys())[:10]
        y_labels = words
        y_pos = np.arange(len(y_labels))

        starts = {}  # starting x pos for each word

        for word in words:
            starts[word] = 0

        for classification in encodings.values():

            y = []
            widths = []
            left = []

            freqs = {}
            for index, word in enumerate(words):
                freqs[word] = cluster_words_classified[cluster][word]

                y.append(index)
                left.append(starts[word])
                classification = str(classification)
                width = int(freqs[word][classification])
                widths.append(width)
                starts[word] += width

            fig.add_trace(go.Bar(
                y=y,
                x=widths,
                orientation='h',
                name=str(classification),
                offset=left,
                marker_color=colors[int(classification)]
            ))

        fig.update_layout(title="Clusters", margin=dict(l=0, r=0, t=30, b=0))

    return fig
