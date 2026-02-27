"""Tensor-related visualization.
"""

import seaborn as sns
import matplotlib.pyplot as plt
import torch


def save_tensor(tensor: torch.Tensor, output_path: str) -> None:
    """Saves a tensor in grayscale mode using Seaborn.

    Args:
        tensor: An input tensor to be saved.
        output_path: An output path to save the tensor.

    """

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        plt.imshow(tensor.cpu().detach().numpy())  # Retain matplotlib for RGB tensors
        plt.xticks([])
        plt.yticks([])
    else:
        sns.heatmap(
            tensor.cpu().detach().numpy(),
            cmap="gray",
            cbar=False,
            xticklabels=False,
            yticklabels=False,
        )

    plt.savefig(output_path)


def show_tensor(tensor: torch.Tensor) -> None:
    """Plots a tensor in grayscale mode using Seaborn.

    Args:
        tensor: An input tensor to be plotted.

    """

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        plt.imshow(tensor.cpu().detach().numpy())  # Retain matplotlib for RGB tensors
        plt.xticks([])
        plt.yticks([])
    else:
        sns.heatmap(
            tensor.cpu().detach().numpy(),
            cmap="gray",
            cbar=False,
            xticklabels=False,
            yticklabels=False,
        )

    plt.show()
