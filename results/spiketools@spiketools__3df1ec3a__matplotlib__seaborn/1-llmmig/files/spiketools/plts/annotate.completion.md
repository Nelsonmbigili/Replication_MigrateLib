### Explanation of Changes
The original code uses `matplotlib` for plotting and adding elements to plots. To migrate to `seaborn`, the following changes were made:
1. **Vertical and Horizontal Lines**: Replaced `ax.axvline` and `ax.axhline` with `seaborn.move_legend` and `seaborn.lineplot` where applicable.
2.