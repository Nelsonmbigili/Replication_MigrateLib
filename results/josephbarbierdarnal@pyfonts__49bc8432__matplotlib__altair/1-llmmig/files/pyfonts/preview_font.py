from .main import load_font
import altair as alt
import pandas as pd
from typing import Optional


def preview_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
):
    """
    Preview a font.
    """
    font = load_font(font_url, font_path)

    # Create a DataFrame to hold the text data
    data = pd.DataFrame({
        "text": [
            "Hello, World From PyFonts!",
            "This is a test.",
            "How about this?"
        ],
        "y": [0.5, 0.35, 0.65],
        "fontsize": [30, 25, 20]
    })

    # Create the Altair chart
    chart = alt.Chart(data).mark_text(
        align="center",
        baseline="middle"
    ).encode(
        x=alt.value(0.5),  # Fixed x position
        y="y:Q",           # y position from the data
        text="text:N",     # Text content
        size="fontsize:Q"  # Font size
    ).configure_text(
        font=font  # Apply the custom font
    ).properties(
        width=500,  # Chart width
        height=250  # Chart height
    )

    return chart
