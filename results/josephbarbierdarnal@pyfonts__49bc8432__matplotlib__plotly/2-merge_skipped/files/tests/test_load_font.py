The provided code does not use `matplotlib` for plotting or visualization purposes. Instead, it imports `FontProperties` from `matplotlib.font_manager` to validate font properties. Since the code does not involve any plotting or visualization, there is no need to migrate it to `plotly`. The `plotly` library is primarily used for creating interactive visualizations, and it does not provide a direct equivalent to `matplotlib.font_manager.FontProperties`.

Thus, no changes are necessary to migrate this code to `plotly`. The code is already functional as is, and replacing `matplotlib.font_manager.FontProperties` with `plotly` would not make sense in this context.

If you have additional code that involves actual plotting or visualization, please provide it, and I can assist with the migration.
def test_load_font_with_url():
    font = load_font(
        font_url="https://github.com/JosephBARBIERDARNAL/pyfonts/blob/main/tests/Ultra-Regular.ttf?raw=true"
    )
    assert isinstance(font, FontProperties)


def test_load_font_with_path():
    font = load_font(font_path="tests/Ultra-Regular.ttf")
    assert isinstance(font, FontProperties)


def test_load_font_invalid_input():
    with pytest.raises(ValueError):
        load_font(font_url="http://example.com/font.ttf", font_path="/path/to/font.ttf")


def test_load_font_no_input():
    with pytest.raises(ValueError):
        load_font()