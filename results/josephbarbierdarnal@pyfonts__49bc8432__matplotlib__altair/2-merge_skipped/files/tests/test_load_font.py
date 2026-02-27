The provided code does not use `matplotlib` for plotting or visualization purposes. Instead, it imports `FontProperties` from `matplotlib.font_manager` and uses it to validate the type of the returned object from the `load_font` function. Since there is no plotting or visualization logic in the code, and `altair` is a visualization library, there is no direct way to migrate this code to use `altair`. 

If the goal is to replace the dependency on `matplotlib` entirely, you would need to replace the use of `FontProperties` with an equivalent functionality from another library or implement a custom solution. However, this would go beyond the scope of simply migrating to `altair`, as `altair` does not provide font management utilities.

If you have additional context or specific requirements for how `altair` should be integrated, please provide that information. Otherwise, the code remains unchanged because it does not involve any functionality that `altair` can replace.
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