### Explanation of Changes
To migrate the code from using `matplotlib` to `altair`, several key changes were made:

1. **Import Statement**: The import statement for `matplotlib.pyplot` was removed and replaced with the import of `altair`.
2. **Data Preparation**: Altair requires data to be in a specific format (usually a DataFrame). I created a DataFrame to hold the text data and their respective positions.
3. **Chart Creation**: Instead of using `plt.text` to add text to the plot, I used Altair's `mark_text` to create text marks. The text properties such as font size and alignment were set using Altair's encoding.
4. **Display**: Instead of `plt.show()`, I used `chart` to display the Altair chart.

Here is the modified code:

```python
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

    # Prepare data for Altair
    data = pd.DataFrame({
        'text': [
            "Hello, World From PyFonts!",
            "This is a test.",
            "How about this?"
        ],
        'y': [0.5, 0.35, 0.65],
        'size': [30, 25, 20]
    })

    # Create the Altair chart
    chart = alt.Chart(data).mark_text(font=font).encode(
        x=alt.X('0:Q', title=None),  # Fixed x position
        y=alt.Y('y:Q', title=None),
        text='text:N',
        size='size:Q',
        align=alt.value('center'),
        baseline=alt.value('middle')
    ).properties(
        width=400,
        height=200
    )

    # Display the chart
    chart.configure_view(stroke=None)  # Remove axis
    chart.display()
```