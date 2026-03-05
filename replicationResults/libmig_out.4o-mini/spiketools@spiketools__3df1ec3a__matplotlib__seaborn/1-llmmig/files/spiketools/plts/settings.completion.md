### Explanation of Changes
To migrate the code from using the `matplotlib` library to the `seaborn` library, the following changes were made:

1. **Import Statement**: The import statement was changed from `import matplotlib.pyplot as plt` to `import seaborn as sns`. This is because `seaborn` is built on top of `matplotlib` and provides a high-level interface for drawing attractive statistical graphics.

2. **Default Colors**: The method to retrieve the default color cycle was updated to use `seaborn`'s functionality. Instead of accessing `plt.rcParams`, we can use `sns.color_palette()` to get the default color palette.

3. **Text Settings**: The text settings remain unchanged as they are compatible with both libraries.

The rest of the code structure and variable names were preserved to maintain compatibility with the larger application.

### Modified Code
```python
"""Default settings for plots."""

import seaborn as sns

###################################################################################################
###################################################################################################

# Define a list of arguments that will be caught and applied with 'set'
SET_KWARGS = ['title', 'xlim', 'ylim', 'xlabel', 'ylabel',
              'xticks', 'yticks', 'xticklabels', 'yticklabels']

# Define a list of other arguments to be caught
OTHER_KWARGS = ['legend']

# Collect a list of the default seaborn color cycle
DEFAULT_COLORS = sns.color_palette()

# Define default settings for plotting text
TEXT_SETTINGS = {'fontdict' : {'fontsize' : 14}, 'ha' : 'center', 'va' : 'center'}

```