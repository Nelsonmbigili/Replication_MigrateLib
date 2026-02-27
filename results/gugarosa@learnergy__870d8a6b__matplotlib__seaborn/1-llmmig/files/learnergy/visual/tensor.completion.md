### Explanation of Changes:
To migrate the code from `matplotlib` to `seaborn`, the following changes were made:
1. **Import Statement**: Replaced `import matplotlib.pyplot as plt` with `import seaborn as sns` and `import matplotlib.pyplot as plt` (since `seaborn` builds on top of `matplotlib`).
2. **Plotting Functions**: Replaced `plt.imshow` with `sns.heatmap` for grayscale tensors. For RGB tensors, `sns` does not directly support `imshow`-like functionality, so `plt.imshow` is retained for RGB tensors.
3. **Color Map**: Used the `cmap` parameter in `sns.heatmap` for grayscale tensors.
4. **Ticks Removal**: Used `sns.heatmap`'s `cbar=False` and `xticklabels=False, yticklabels=False` to remove ticks and color bars, replacing `plt.xticks([])` and `plt.yticks([])`.

### Modified Code:
```python
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
```

### Key Notes:
- `sns.heatmap` is used for grayscale tensors because it provides better integration with `seaborn`'s functionality.
- For RGB tensors, `plt.imshow` is retained because `seaborn` does not natively support RGB image plotting.
- The overall structure and logic of the code remain unchanged to ensure compatibility with the larger application.