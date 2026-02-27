"""Tensor-related visualization.
"""

import altair as alt
import pandas as pd
import torch


def save_tensor(tensor: torch.Tensor, output_path: str) -> None:
    """Saves a tensor in grayscale mode using Altair.

    Args:
        tensor: An input tensor to be saved.
        output_path: An output path to save the tensor.

    """

    # Prepare tensor data for Altair
    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)  # Convert to HWC format
        data = pd.DataFrame(
            tensor.cpu().detach().numpy().reshape(-1, 3),
            columns=["R", "G", "B"]
        )
        data["x"] = [i % tensor.size(2) for i in range(tensor.numel() // 3)]
        data["y"] = [i // tensor.size(2) for i in range(tensor.numel() // 3)]
        chart = alt.Chart(data).mark_image().encode(
            x="x:O",
            y="y:O",
            color=alt.Color("R:G", scale=None)  # RGB color
        )
    else:
        data = pd.DataFrame({
            "value": tensor.cpu().detach().numpy().flatten(),
            "x": [i % tensor.size(1) for i in range(tensor.numel())],
            "y": [i // tensor.size(1) for i in range(tensor.numel())],
        })
        chart = alt.Chart(data).mark_rect().encode(
            x="x:O",
            y="y:O",
            color=alt.Color("value:Q", scale=alt.Scale(scheme="gray"))
        )

    # Remove axes and save the chart
    chart = chart.properties(width=tensor.size(-1), height=tensor.size(-2)).configure_axis(
        grid=False, domain=False, ticks=False, labels=False
    )
    chart.save(output_path)


def show_tensor(tensor: torch.Tensor) -> None:
    """Plots a tensor in grayscale mode using Altair.

    Args:
        tensor: An input tensor to be plotted.

    """

    # Prepare tensor data for Altair
    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)  # Convert to HWC format
        data = pd.DataFrame(
            tensor.cpu().detach().numpy().reshape(-1, 3),
            columns=["R", "G", "B"]
        )
        data["x"] = [i % tensor.size(2) for i in range(tensor.numel() // 3)]
        data["y"] = [i // tensor.size(2) for i in range(tensor.numel() // 3)]
        chart = alt.Chart(data).mark_image().encode(
            x="x:O",
            y="y:O",
            color=alt.Color("R:G", scale=None)  # RGB color
        )
    else:
        data = pd.DataFrame({
            "value": tensor.cpu().detach().numpy().flatten(),
            "x": [i % tensor.size(1) for i in range(tensor.numel())],
            "y": [i // tensor.size(1) for i in range(tensor.numel())],
        })
        chart = alt.Chart(data).mark_rect().encode(
            x="x:O",
            y="y:O",
            color=alt.Color("value:Q", scale=alt.Scale(scheme="gray"))
        )

    # Remove axes and display the chart
    chart = chart.properties(width=tensor.size(-1), height=tensor.size(-2)).configure_axis(
        grid=False, domain=False, ticks=False, labels=False
    )
    chart.show()
