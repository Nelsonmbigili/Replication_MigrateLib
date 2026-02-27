from .main import load_font
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional


def preview_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
):
    """
    Preview a font.
    """
    # Load the font
    font = load_font(font_url, font_path)

    # Set the seaborn theme
    sns.set_theme(style="white")

    # Create the figure
    plt.figure(figsize=(10, 5))

    # Add text to the plot
    plt.text(
        0.5,
        0.5,
        "Hello, World From PyFonts!",
        fontsize=30,
        ha="center",
        va="center",
        font=font,
    )
    plt.text(
        0.5,
        0.35,
        "This is a test.",
        fontsize=25,
        ha="center",
        va="center",
        font=font,
    )
    plt.text(
        0.5,
        0.65,
        "How about this?",
        fontsize=20,
        ha="center",
        va="center",
        font=font,
    )

    # Hide the axes
    plt.axis("off")

    # Show the plot
    plt.show()
