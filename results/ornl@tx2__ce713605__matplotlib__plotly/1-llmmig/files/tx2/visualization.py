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
