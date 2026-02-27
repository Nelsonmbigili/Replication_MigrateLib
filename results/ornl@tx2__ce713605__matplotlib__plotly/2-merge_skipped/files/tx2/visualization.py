"""Helper functions for constructing visualizations."""

import itertools
import math
import base64
from io import BytesIO
from typing import Dict, List, Union

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from wordcloud import WordCloud
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import tx2.wrapper
from tx2 import calc, utils, STOPWORDS


def _wordcloud_to_base64(wordcloud):
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
    """Convert a WordCloud object to a base64-encoded image for Plotly."""
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    return f"data:image/png;base64,{img_str}"


def plot_big_wordcloud(index: int, clusters: Dict[str, List[int]]):
    """Render the word cloud that the currently selected point is in using Plotly."""
    cluster = utils.which_cluster(index, clusters)
    wordcloud_image = _wordcloud_to_base64(_cached_wordclouds[cluster])

    fig = go.Figure()
    fig.add_trace(
        go.Image(source=wordcloud_image)
    )
    fig.update_layout(
        title=str(cluster),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig


def plot_passed_wordcloud(cloud, name):
    """Render the given word cloud using Plotly."""
    wordcloud_image = _wordcloud_to_base64(cloud)

    fig = go.Figure()
    fig.add_trace(
        go.Image(source=wordcloud_image)
    )
    fig.update_layout(
        title=name,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig


def plot_wordclouds(dashboard):
    """Render the grid of all wordclouds using Plotly."""
    num_cols = 4
    num_rows = max(math.ceil(len(dashboard.transformer_wrapper.clusters) / num_cols), 2)

    fig = make_subplots(rows=num_rows, cols=num_cols)

    for index, cluster in enumerate(dashboard.transformer_wrapper.clusters):
        row = index // num_cols + 1
        col = index % num_cols + 1
        wordcloud_image = _wordcloud_to_base64(_cached_wordclouds[cluster])
        fig.add_trace(
            go.Image(source=wordcloud_image),
            row=row,
            col=col,
        )
        fig.add_annotation(
            text=str(cluster),
            xref=f"x{index + 1}",
            yref=f"y{index + 1}",
            showarrow=False,
            x=0.5,
            y=1.1,
            xanchor="center",
            yanchor="bottom",
        )

    fig.update_layout(
        height=num_rows * 200,
        width=800,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


def plot_confusion_matrix(
    pred_y: List[int], target_y: List[int], encodings: Dict[str, int], figsize=(800, 800)
):
    """Get the confusion matrix for given predictions using Plotly."""
    labels = []
    for i in range(len(encodings.keys())):
        for key, value in encodings.items():
            if value == i:
                labels.append(key)
                break
    cm = confusion_matrix(target_y, pred_y, labels=list(encodings.values()))

    acc = np.trace(cm) / float(np.sum(cm))
    miss = 1 - acc

    fig = go.Figure(
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(cm, interpolation="nearest", cmap="Blues")

    tick_marks = np.arange(len(labels))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(labels, rotation=90)
    #     for tick in ax.get_xticklabels():
    #         tick.set_rotation(45)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(labels)
    ax.set_xlabel(
        "Predicted label\naccuracy={:0.4f}; misclassified={:0.4f}".format(acc, miss)
    )
    ax.set_ylabel("True label")
    ax.grid(False)

    text_fg_threshold = cm.max() / 1.5
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        ax.text(
            j,
            i,
            "{:,}".format(cm[i, j]),
            horizontalalignment="center",
            color="white" if cm[i, j] > text_fg_threshold else "black",
        )

    fig.patch.set_facecolor("white")
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
    fig, ax = plt.subplots(figsize=(10, 8))

    # render all test data projections
    if not dashboard.chk_focus_errors.value:
        testing_x, testing_y, testing_c = _get_scatter_points_from_embeddings(
            dashboard.colors,
            np.array(dashboard.transformer_wrapper.projections_testing),
            dashboard.transformer_wrapper.test_labels,
        )
        ax.scatter(
            x=testing_x, y=testing_y, c=testing_c, alpha=0.8, s=dashboard.point_size
        )
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
        ax.scatter(
            x=incorrect_x,
            y=incorrect_y,
            c=incorrect_c,
            alpha=0.8,
            s=dashboard.point_size,
        )
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
        ax.scatter(
            x=correct_x,
            y=correct_y,
            c=correct_c,
            alpha=0.1,
            s=dashboard.unfocused_point_size,
        )

    # render training data projections
    if dashboard.chk_show_train.value:
        training_x, training_y, training_c = _get_scatter_points_from_embeddings(
            dashboard.colors,
            np.array(dashboard.transformer_wrapper.projections_training),
            dashboard.transformer_wrapper.train_labels,
        )
        ax.scatter(
            x=training_x,
            y=training_y,
            c=training_c,
            alpha=0.1,
            s=dashboard.unfocused_point_size,
        )

    # render highlighted data points
    if len(dashboard.highlight_indices) > 0:
        ax.scatter(
            x=testing_x[dashboard.highlight_indices],
            y=testing_y[dashboard.highlight_indices],
            c=testing_c[dashboard.highlight_indices],
            s=dashboard.highlighted_point_size,
            edgecolors="red",
            linewidth=2,
        )

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
        ax.scatter(
            x=text_projection[0],
            y=text_projection[1],
            s=dashboard.highlighted_point_size,
            c=pred_color,
            edgecolors="black",
            linewidth=2,
        )

    # render the original reference point and arrow if applicable
    if dashboard.prior_reference_point is not None:
        ax.scatter(
            x=dashboard.prior_reference_point[0][0],
            y=dashboard.prior_reference_point[0][1],
            s=dashboard.highlighted_point_size,
            c=dashboard.prior_reference_point[1],
            edgecolors="black",
            linewidth=2,
        )

        # arrow!
        if dashboard.prior_reference_text != text:
            x_dist = text_projection[0] - dashboard.prior_reference_point[0][0]
            y_dist = text_projection[1] - dashboard.prior_reference_point[0][1]
            #             if abs(x_dist) + abs(y_dist) > .5:
            width = 0.15
            head_width = 0.65
            ax.arrow(
                dashboard.prior_reference_point[0][0],
                dashboard.prior_reference_point[0][1],
                x_dist,
                y_dist,
                width=width,
                length_includes_head=True,
                head_width=head_width,
                facecolor="black",
                edgecolor="white",
            )

    # show visual cluster labels
    if dashboard.chk_show_cluster_labels.value:
        for x, y, label in dashboard.transformer_wrapper.cluster_labels:
            ax.text(
                float(x),
                float(y),
                label,
                bbox={"facecolor": "white", "alpha": 0.5, "pad": 2},
            )

    # display legend
    legend_elements = []
    for i in range(0, len(dashboard.transformer_wrapper.encodings)):
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label=list(dashboard.transformer_wrapper.encodings.keys())[i],
                markerfacecolor=dashboard.colors[i],
                markersize=10,
            )
        )
    ax.legend(handles=legend_elements)

    # output
    fig.patch.set_facecolor("white")
    fig.tight_layout()

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
        data=go.Heatmap(
            z=cm,
            x=labels,
            y=labels,
            colorscale="Blues",
            showscale=True,
            texttemplate="%{z}",
            textfont={"size": 10},
        )
    )
    fig.update_layout(
        title=f"Confusion Matrix<br>Accuracy={acc:.4f}; Misclassified={miss:.4f}",
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
        xaxis=dict(tickangle=45),
        yaxis=dict(tickangle=0),
        margin=dict(l=50, r=50, t=100, b=50),
    )
    return fig


def plot_clusters(clusters, cluster_values):
    """Plot highest word values for each cluster using Plotly."""
    num_cols = 4
    num_rows = math.ceil(len(clusters) / num_cols)

    fig = make_subplots(rows=num_rows, cols=num_cols)

    for index, cluster in enumerate(clusters):
        row = index // num_cols + 1
        col = index % num_cols + 1
        freq = cluster_values[cluster][:10]
        y = [item[1] for item in freq]
        y_labels = [item[0][:20] for item in freq]
        y_pos = list(range(len(y_labels)))

        fig.add_trace(
            go.Bar(
                x=y,
                y=y_labels,
                orientation="h",
                name=str(cluster),
            ),
            row=row,
            col=col,
        )

    fig.update_layout(
        height=num_rows * 200,
        width=800,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


def plot_clusters_stacked(clusters, cluster_words_classified, encodings, colors):
    """Plot highest word values for each cluster, colored according to entry classification using Plotly."""
    num_cols = 4
    num_rows = math.ceil(len(clusters) / num_cols)

    fig = make_subplots(rows=num_rows, cols=num_cols)

    for index, cluster in enumerate(clusters):
        row = index // num_cols + 1
        col = index % num_cols + 1

        words = list(cluster_words_classified[cluster].keys())[:10]
        y_labels = words
        y_pos = list(range(len(y_labels)))

        starts = {word: 0 for word in words}

        for classification, color in zip(encodings.values(), colors):
            y = []
            widths = []
            for word in words:
                width = cluster_words_classified[cluster][word].get(str(classification), 0)
                y.append(word)
                widths.append(width)
                starts[word] += width

            fig.add_trace(
                go.Bar(
                    x=widths,
                    y=y,
                    orientation="h",
                    marker_color=color,
                    name=str(classification),
                ),
                row=row,
                col=col,
            )

    fig.update_layout(
        height=num_rows * 200,
        width=800,
        showlegend=True,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig