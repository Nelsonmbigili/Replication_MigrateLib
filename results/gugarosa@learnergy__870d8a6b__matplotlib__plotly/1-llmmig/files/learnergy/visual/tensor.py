"""Tensor-related visualization.
"""

import plotly.graph_objects as go
import torch


def save_tensor(tensor: torch.Tensor, output_path: str) -> None:
    """Saves a tensor in grayscale mode using Plotly.

    Args:
        tensor: An input tensor to be saved.
        output_path: An output path to save the tensor.

    """

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        image_data = tensor.cpu().detach().numpy()
    else:
        image_data = tensor.cpu().detach().numpy()

    fig = go.Figure(go.Image(z=image_data))
    fig.write_image(output_path)


def show_tensor(tensor: torch.Tensor) -> None:
    """Plots a tensor in grayscale mode using Plotly.

    Args:
        tensor: An input tensor to be plotted.

    """

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        image_data = tensor.cpu().detach().numpy()
    else:
        image_data = tensor.cpu().detach().numpy()

    fig = go.Figure(go.Image(z=image_data))
    fig.show()
