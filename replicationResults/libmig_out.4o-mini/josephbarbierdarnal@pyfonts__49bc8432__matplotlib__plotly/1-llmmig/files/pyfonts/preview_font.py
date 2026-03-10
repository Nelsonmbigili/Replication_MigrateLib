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

    fig = go.Figure()

    fig.add_annotation(
        x=0.5,
        y=0.5,
        text="Hello, World From PyFonts!",
        font=dict(size=30, family=font),
        showarrow=False,
        xref="paper",
        yref="paper",
        align="center"
    )
    fig.add_annotation(
        x=0.5,
        y=0.35,
        text="This is a test.",
        font=dict(size=25, family=font),
        showarrow=False,
        xref="paper",
        yref="paper",
        align="center"
    )
    fig.add_annotation(
        x=0.5,
        y=0.65,
        text="How about this?",
        font=dict(size=20, family=font),
        showarrow=False,
        xref="paper",
        yref="paper",
        align="center"
    )

    fig.show()
