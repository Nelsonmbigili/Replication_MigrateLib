"""Default settings for plots."""

import plotly.graph_objects as go
import plotly.colors

###################################################################################################
###################################################################################################

# Define a list of arguments that will be caught and applied with 'set'
SET_KWARGS = ['title', 'xlim', 'ylim', 'xlabel', 'ylabel',
              'xticks', 'yticks', 'xticklabels', 'yticklabels']

# Define a list of other arguments to be caught
OTHER_KWARGS = ['legend']

# Collect a list of the default plotly color cycle
DEFAULT_COLORS = plotly.colors.qualitative.Plotly

# Define default settings for plotting text
TEXT_SETTINGS = {'fontdict' : {'fontsize' : 14}, 'ha' : 'center', 'va' : 'center'}

