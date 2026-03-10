### Explanation of Changes
To migrate the code from using `matplotlib` to `plotly`, the following changes were made:

1. **Import Statement**: The import for `matplotlib.pyplot` was replaced with `import plotly.graph_objects as go`.
2. **Figure Creation**: Instead of using `plt.figure()`, a `plotly` figure object was created using `go.Figure()`.
3. **Text Annotations**: The `plt.text()` calls were replaced with `fig.add_annotation()` to add text annotations to the figure.
4. **Axis Visibility**: The `plt.axis("off")` call was removed, as `plotly` does not require this for hiding axes.
5. **Displaying the Figure**: The `plt.show()` call was replaced with `fig.show()` to display the plot.

Here is the modified code:

```python
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
```