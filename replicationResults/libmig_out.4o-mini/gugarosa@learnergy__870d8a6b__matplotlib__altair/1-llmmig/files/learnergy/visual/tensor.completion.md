### Explanation of Changes
To migrate the code from using `matplotlib` to `altair`, the following changes were made:

1. **Import Statement**: The import statement for `matplotlib.pyplot` was replaced with the import statement for `altair`.
2. **Data Preparation**: The tensor data was converted to a format suitable for `altair`, specifically using a Pandas DataFrame to hold the pixel values.
3. **Visualization**: The plotting functions were replaced with `altair` charting methods. `altair` uses a declarative approach to create visualizations, so the code was adjusted to create a heatmap for grayscale images and a color image for RGB images.
4. **Saving and Showing**: The methods for saving and displaying the visualizations were adapted to use `altair`'s capabilities.

Here is the modified code:

```python
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
    
    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        tensor = tensor.cpu().detach().numpy()
    else:
        tensor = tensor.cpu().detach().numpy()

    # Convert tensor to DataFrame
    height, width = tensor.shape[:2]
    data = pd.DataFrame({
        'x': [],
        'y': [],
        'value': []
    })

    for i in range(height):
        for j in range(width):
            data = data.append({'x': j, 'y': i, 'value': tensor[i, j] if tensor.ndim == 2 else tensor[i, j, 0]}, ignore_index=True)

    # Create a heatmap for grayscale or color image
    chart = alt.Chart(data).mark_rect().encode(
        x='x:O',
        y='y:O',
        color=alt.Color('value:Q', scale=alt.Scale(scheme='gray' if tensor.ndim == 2 else 'viridis'))
    ).properties(width=width, height=height)

    chart.save(output_path)


def show_tensor(tensor: torch.Tensor) -> None:
    """Plots a tensor in grayscale mode using Altair.

    Args:
        tensor: An input tensor to be plotted.

    """
    
    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        tensor = tensor.cpu().detach().numpy()
    else:
        tensor = tensor.cpu().detach().numpy()

    # Convert tensor to DataFrame
    height, width = tensor.shape[:2]
    data = pd.DataFrame({
        'x': [],
        'y': [],
        'value': []
    })

    for i in range(height):
        for j in range(width):
            data = data.append({'x': j, 'y': i, 'value': tensor[i, j] if tensor.ndim == 2 else tensor[i, j, 0]}, ignore_index=True)

    # Create a heatmap for grayscale or color image
    chart = alt.Chart(data).mark_rect().encode(
        x='x:O',
        y='y:O',
        color=alt.Color('value:Q', scale=alt.Scale(scheme='gray' if tensor.ndim == 2 else 'viridis'))
    ).properties(width=width, height=height)

    chart.display()
``` 

This code now uses `altair` for visualizing tensors, maintaining the original structure and functionality while adapting to the new library's requirements.