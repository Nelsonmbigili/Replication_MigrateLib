"""Default settings for plots."""

import altair as alt

###################################################################################################
###################################################################################################

# Define a list of arguments that will be caught and applied with 'set'
SET_KWARGS = ['title', 'xlim', 'ylim', 'xlabel', 'ylabel',
              'xticks', 'yticks', 'xticklabels', 'yticklabels']

# Define a list of other arguments to be caught
OTHER_KWARGS = ['legend']

# Collect a list of the default Altair color cycle
DEFAULT_COLORS = alt.themes.get()  # Altair uses themes for color schemes

# Define default settings for plotting text
TEXT_SETTINGS = {'fontSize': 14, 'align': 'center', 'baseline': 'middle'}

