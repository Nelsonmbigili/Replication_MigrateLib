### Explanation of Changes
To migrate the code from using `matplotlib` to `plotly`, the following changes were made:

1. **Import Statement**: The import statement for `matplotlib.pyplot` was replaced with the import statement for `plotly.graph_objects` as `go`.
2. **Figure Creation**: The `plt.figure()` calls were removed since `plotly` does not require explicit figure creation.
3. **Image Display**: The `plt.imshow()` function was replaced with `go.Figure()` and `go.Image()` to create an image plot in `plotly`.
4. **Saving the Image**: The `plt.savefig()` function was replaced with `fig.write_image()` to save the figure.
5. **Showing the Image**: The `plt.show()` function was replaced with `fig.show()` to display the figure.

The overall structure of the functions remains the same, but the plotting and saving methods are now compatible with `plotly`.

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

    fig = go.Figure(data=go.Image(z=image_data))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
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

    fig = go.Figure(data=go.Image(z=image_data))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.show()
```