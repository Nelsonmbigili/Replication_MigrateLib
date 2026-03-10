"""Default settings for plots."""

import altair as alt

###################################################################################################
###################################################################################################

# Define a list of arguments that will be caught and applied with 'set'
SET_KWARGS = ['title', 'xlim', 'ylim', 'xlabel', 'ylabel',
              'xticks', 'yticks', 'xticklabels', 'yticklabels']

# Define a list of other arguments to be caught
OTHER_KWARGS = ['legend']

# Collect a list of the default altair color scheme
DEFAULT_COLORS = alt.themes.get_default_colors()

# Define default settings for plotting text
# Note: Altair handles text settings differently, so this may not be directly applicable.
