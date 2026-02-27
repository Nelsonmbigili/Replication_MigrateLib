The following Python code currently uses the library "matplotlib" version 3.10.1.
Migrate this code to use the library "seaborn" version 0.13.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "matplotlib" to "seaborn".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "matplotlib" and "seaborn".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""Tensor-related visualization.
"""

import matplotlib.pyplot as plt
import torch


def save_tensor(tensor: torch.Tensor, output_path: str) -> None:
    """Saves a tensor in grayscale mode using Matplotlib.

    Args:
        tensor: An input tensor to be saved.
        output_path: An outputh path to save the tensor.

    """

    plt.figure()

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        plt.imshow(tensor.cpu().detach().numpy())
    else:
        plt.imshow(tensor.cpu().detach().numpy(), cmap=plt.cm.get_cmap("gray"))

    plt.xticks([])
    plt.yticks([])

    plt.savefig(output_path)


def show_tensor(tensor: torch.Tensor) -> None:
    """Plots a tensor in grayscale mode using Matplotlib.

    Args:
        tensor: An input tensor to be plotted.

    """

    plt.figure()

    if tensor.size(0) == 3:
        tensor = tensor.permute(1, 2, 0)
        plt.imshow(tensor.cpu().detach().numpy())
    else:
        plt.imshow(tensor.cpu().detach().numpy(), cmap=plt.cm.get_cmap("gray"))

    plt.xticks([])
    plt.yticks([])

    plt.show()

```