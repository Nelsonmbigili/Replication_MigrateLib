from .main import load_font
import plotly.graph_objects as go
from typing import Optional


def preview_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
):
    """
    Preview a font.
    """
    font = load_font(font_url, font_path)

    # Create a Plotly figure
    fig = go.Figure()

    # Add text annotations
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text="Hello, World From PyFonts!",
        font=dict(size=30, family=font),
        showarrow=False,
        xanchor="center",
        yanchor="middle",
    )
    fig.add_annotation(
        x=0.5,
        y=0.35,
        text="This is a test.",
        font=dict(size=25, family=font),
        showarrow=False,
        xanchor="center",
        yanchor="middle",
    )
    fig.add_annotation(
        x=0.5,
        y=0.65,
        text="How about this?",
        font=dict(size=20, family=font),
        showarrow=False,
        xanchor="center",
        yanchor="middle",
    )

    # Update layout to hide axes
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        width=1000,
        height=500,
    )

    # Show the figure
    fig.show()
