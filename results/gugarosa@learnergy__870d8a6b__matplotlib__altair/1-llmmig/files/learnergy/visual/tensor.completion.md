### Explanation of Changes:
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. **Altair Import**: Replaced the `matplotlib.pyplot` import with `altair` since Altair is now used for visualization.
2. **Data Preparation**: Altair requires data in a tabular format (e.g., pandas DataFrame). The tensor data is converted into a DataFrame for visualization.
3. **Grayscale Handling**: Altair does not have a direct `cmap` parameter like Matplotlib. Instead, we use Altair's `color` encoding with a grayscale color scheme for single-channel tensors.
4. **Image Display**: Altair uses `mark_image()` for image visualization. The tensor data is reshaped and passed as a DataFrame to Altair's chart.
5. **Saving Charts**: Altair charts are saved using the `save()` method, which supports various formats like PNG, SVG, etc.
6. **Axis Removal**: Altair does not have `xticks` or `yticks` like Matplotlib. Instead, we use `properties()` to remove axes by setting `axis=None`.

### Modified Code:
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
```

### Key Notes:
- The tensor data is reshaped into a tabular format (DataFrame) for Altair.
- The `mark_image()` is used for RGB tensors, while `mark_rect()` is used for grayscale tensors.
- Axis ticks and labels are removed using `configure_axis()`.
- The `save()` method is used to save the chart to the specified output path.