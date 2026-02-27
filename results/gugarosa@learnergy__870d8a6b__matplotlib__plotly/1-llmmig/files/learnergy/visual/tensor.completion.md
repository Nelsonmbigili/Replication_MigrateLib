### Explanation of Changes
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. Replaced `matplotlib.pyplot` with `plotly.graph_objects` (`plotly.graph_objects.Figure`).
2. Used `plotly.graph_objects.Image` to display the tensor as an image.
3. Removed `plt.xticks([])` and `plt.yticks([])` since `plotly` does not require explicit disabling of ticks for this use case.
4. Replaced `plt.savefig` with `fig.write_image` for saving the tensor visualization.
5. Replaced `plt.show()` with `fig.show()` for displaying the tensor visualization.
6. Ensured that the tensor data is converted to a NumPy array and passed to `plotly.graph_objects.Image`.

Below is the modified code:

### Modified Code
```python
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
```

### Key Notes
- The `plotly.graph_objects.Image` automatically handles both grayscale and RGB images, so no need to specify a colormap explicitly.
- The `fig.write_image` method requires the `kaleido` package to be installed for saving images. Ensure that `kaleido` is installed in your environment (`pip install -U kaleido`).
- The tensor data is converted to a NumPy array before being passed to `plotly` for compatibility.