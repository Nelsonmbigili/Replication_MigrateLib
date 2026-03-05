### Explanation of Changes
To migrate the code from using `matplotlib` to `seaborn`, I made the following changes:
1. **Import Statement**: I replaced the import of `matplotlib.pyplot` with `seaborn`. Since `seaborn` is built on top of `matplotlib`, it can still utilize `matplotlib` functions, but for the purpose of this migration, I will keep the code focused on `seaborn`.
2. **Image Display**: The `imshow` function from `matplotlib` is still used, as `seaborn` does not provide a direct equivalent for displaying images. However, the colormap can be simplified by using `cmap='gray'` directly in the `imshow` function.
3. **Figure Creation**: The figure creation remains the same, as `seaborn` does not change how figures are created in `matplotlib`.

Here is the modified code:

```python
"""Tensor-related visualization.
"""

import seaborn as sns
import torch


def save_tensor(tensor: torch.Tensor, output_path: str) -> None:
    """Saves a tensor in grayscale mode using Seaborn.

    Args:
        tensor: An input tensor to be saved.
        output_path: An output path to save the tensor.

    """

    plt.figure()

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        plt.imshow(tensor.cpu().detach().numpy())
    else:
        plt.imshow(tensor.cpu().detach().numpy(), cmap='gray')

    plt.xticks([])
    plt.yticks([])

    plt.savefig(output_path)


def show_tensor(tensor: torch.Tensor) -> None:
    """Plots a tensor in grayscale mode using Seaborn.

    Args:
        tensor: An input tensor to be plotted.

    """

    plt.figure()

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        plt.imshow(tensor.cpu().detach().numpy())
    else:
        plt.imshow(tensor.cpu().detach().numpy(), cmap='gray')

    plt.xticks([])
    plt.yticks([])

    plt.show()
```

Note: The code still uses `plt` for figure creation and image display, as `seaborn` does not replace these functionalities. The primary change is the import statement.