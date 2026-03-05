"""Helper functions for constructing visualizations."""

import itertools
import math
from typing import Dict, List, Union

import altair as alt
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
    wordcloud_data = _cached_wordclouds[cluster].to_array()
    wordcloud_df = pd.DataFrame(wordcloud_data)

    chart = alt.Chart(wordcloud_df).mark_image().encode(
        x='x:Q',
        y='y:Q',
        url='url:N'
    ).properties(
        width=800,
        height=400
    )

    return chart


def plot_passed_wordcloud(cloud, name):
    """Render the given word cloud.

    :param cloud: The word cloud to render.
    :param name: The title to render with the word cloud.
    """
    wordcloud_data = cloud.to_array()
    wordcloud_df = pd.DataFrame(wordcloud_data)

    chart = alt.Chart(wordcloud_df).mark_image().encode(
        x='x:Q',
        y='y:Q',
        url='url:N'
    ).properties(
        width=800,
        height=400
    )

    return chart


def plot_wordclouds(dashboard):
    """Render the grid of all wordclouds.

    :param dashboard: The current dashboard, needed in order to grab the cluster data.
    """
    num_cols = 4
    num_rows = max(math.ceil(len(dashboard.transformer_wrapper.clusters) / num_cols), 2)

    charts = []
    for index, cluster in enumerate(dashboard.transformer_wrapper.clusters):
        wordcloud_data = _cached_wordclouds[cluster].to_array()
        wordcloud_df = pd.DataFrame(wordcloud_data)

        chart = alt.Chart(wordcloud_df).mark_image().encode(
            x='x:Q',
            y='y:Q',
            url='url:N'
        ).properties(
            width=200,
            height=100
        ).properties(title=str(cluster))

        charts.append(chart)

    return alt.vconcat(*charts).resolve_scale(
        color='independent'
    )


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

    cm_df = pd.DataFrame(cm, index=labels, columns=labels)

    chart = alt.Chart(cm_df.reset_index().melt(id_vars='index')).mark_rect().encode(
        x='variable:N',
        y='index:N',
        color=alt.Color('value:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['index:N', 'variable:N', 'value:Q']
    ).properties(
        width=400,
        height=400
    )

    return chart


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

    # render all test data projections
    if not dashboard.chk_focus_errors.value:
        testing_x, testing_y, testing_c = _get_scatter_points_from_embeddings(
            dashboard.colors,
            np.array(dashboard.transformer_wrapper.projections_testing),
            dashboard.transformer_wrapper.test_labels,
        )
        df_testing = pd.DataFrame({
            'x': testing_x,
            'y': testing_y,
            'color': testing_c
        })
        scatter_chart = alt.Chart(df_testing).mark_circle().encode(
            x='x:Q',
            y='y:Q',
            color='color:N',
            tooltip=['x', 'y']
        ).properties(
            width=600,
            height=400
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
        df_incorrect = pd.DataFrame({
            'x': incorrect_x,
            'y': incorrect_y,
            'color': incorrect_c
        })
        scatter_chart = alt.Chart(df_incorrect).mark_circle().encode(
            x='x:Q',
            y='y:Q',
            color='color:N',
            tooltip=['x', 'y']
        ).properties(
            width=600,
            height=400
        )

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
        df_correct = pd.DataFrame({
            'x': correct_x,
            'y': correct_y,
            'color': correct_c
        })
        scatter_chart += alt.Chart(df_correct).mark_circle(opacity=0.1).encode(
            x='x:Q',
            y='y:Q',
            color='color:N',
            tooltip=['x', 'y']
        )

    # render training data projections
    if dashboard.chk_show_train.value:
        training_x, training_y, training_c = _get_scatter_points_from_embeddings(
            dashboard.colors,
            np.array(dashboard.transformer_wrapper.projections_training),
            dashboard.transformer_wrapper.train_labels,
        )
        df_training = pd.DataFrame({
            'x': training_x,
            'y': training_y,
            'color': training_c
        })
        scatter_chart += alt.Chart(df_training).mark_circle(opacity=0.1).encode(
            x='x:Q',
            y='y:Q',
            color='color:N',
            tooltip=['x', 'y']
        )

    # render highlighted data points
    if len(dashboard.highlight_indices) > 0:
        highlighted_x = testing_x[dashboard.highlight_indices]
        highlighted_y = testing_y[dashboard.highlight_indices]
        highlighted_c = testing_c[dashboard.highlight_indices]
        df_highlighted = pd.DataFrame({
            'x': highlighted_x,
            'y': highlighted_y,
            'color': highlighted_c
        })
        scatter_chart += alt.Chart(df_highlighted).mark_circle(size=100, stroke='red', strokeWidth=2).encode(
            x='x:Q',
            y='y:Q',
            color='color:N',
            tooltip=['x', 'y']
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
        df_new_point = pd.DataFrame({
            'x': [text_projection[0]],
            'y': [text_projection[1]],
            'color': [pred_color]
        })
        scatter_chart += alt.Chart(df_new_point).mark_circle(size=100, stroke='black', strokeWidth=2).encode(
            x='x:Q',
            y='y:Q',
            color='color:N',
            tooltip=['x', 'y']
        )

    # render the original reference point and arrow if applicable
    if dashboard.prior_reference_point is not None:
        df_ref_point = pd.DataFrame({
            'x': [dashboard.prior_reference_point[0][0]],
            'y': [dashboard.prior_reference_point[0][1]],
            'color': [dashboard.prior_reference_point[1]]
        })
        scatter_chart += alt.Chart(df_ref_point).mark_circle(size=100, stroke='black', strokeWidth=2).encode(
            x='x:Q',
            y='y:Q',
            color='color:N',
            tooltip=['x', 'y']
        )

        # arrow!
        if dashboard.prior_reference_text != text:
            x_dist = text_projection[0] - dashboard.prior_reference_point[0][0]
            y_dist = text_projection[1] - dashboard.prior_reference_point[0][1]
            arrow_data = pd.DataFrame({
                'x': [dashboard.prior_reference_point[0][0]],
                'y': [dashboard.prior_reference_point[0][1]],
                'x_end': [text_projection[0]],
                'y_end': [text_projection[1]]
            })
            arrow_chart = alt.Chart(arrow_data).mark_rule().encode(
                x='x:Q',
                x2='x_end:Q',
                y='y:Q',
                y2='y_end:Q',
                color=alt.value('black')
            )
            scatter_chart += arrow_chart

    # show visual cluster labels
    if dashboard.chk_show_cluster_labels.value:
        for x, y, label in dashboard.transformer_wrapper.cluster_labels:
            scatter_chart += alt.Chart(pd.DataFrame({'x': [float(x)], 'y': [float(y)], 'label': [label]})).mark_text(
                align='center',
                baseline='middle',
                dx=5,
                dy=-5
            ).encode(
                x='x:Q',
                y='y:Q',
                text='label:N'
            )

    # display legend
    legend_data = pd.DataFrame({
        'label': list(dashboard.transformer_wrapper.encodings.keys()),
        'color': [dashboard.colors[i] for i in range(len(dashboard.transformer_wrapper.encodings))]
    })
    legend_chart = alt.Chart(legend_data).mark_point().encode(
        x=alt.X('label:N', title='Classes'),
        y=alt.Y('color:N', title='Colors'),
        color='color:N'
    )

    # output
    dashboard.html_graph_status.value = (
        "<p>" + tx2.visualization.get_nice_html_label("Ready!", "#008000") + "</p>"
    )

    return scatter_chart + legend_chart


def plot_clusters(clusters, cluster_values):
    """Plot highest word values for each cluster."""
    num_cols = 4

    num_rows = math.ceil(len(clusters) / num_cols)

    charts = []
    for index, cluster in enumerate(clusters):
        freq = cluster_values[cluster][:10]
        y = [item[1] for item in freq]
        y_labels = [item[0][:20] for item in freq]
        y_pos = np.arange(len(y_labels))

        df_cluster = pd.DataFrame({
            'y': y,
            'y_labels': y_labels
        })

        chart = alt.Chart(df_cluster).mark_bar().encode(
            y=alt.Y('y_labels:N', sort='-x'),
            x='y:Q'
        ).properties(
            title=str(cluster),
            width=200,
            height=100
        )

        charts.append(chart)

    return alt.vconcat(*charts).resolve_scale(
        color='independent'
    )


def plot_clusters_stacked(clusters, cluster_words_classified, encodings, colors):
    """Plot highest word values for each cluster, colored according to entry classification"""
    num_cols = 4

    num_rows = math.ceil(len(clusters) / num_cols)

    charts = []
    for index, cluster in enumerate(clusters):
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

            df_stacked = pd.DataFrame({
                'y': y,
                'widths': widths,
                'left': left,
                'color': [colors[int(classification)]] * len(y)
            })

            chart = alt.Chart(df_stacked).mark_bar().encode(
                y='y:O',
                x='widths:Q',
                color='color:N',
                xOffset='left:Q'
            ).properties(
                title=str(cluster),
                width=200,
                height=100
            )

            charts.append(chart)

    return alt.vconcat(*charts).resolve_scale(
        color='independent'
    )
