### Explanation of Changes:
To migrate the code from using `beautifulsoup4` to `pyquery`, the following changes were made:
1. **Replace `soup_from_str`**: The `soup_from_str` utility function, which likely uses BeautifulSoup to parse HTML strings, was replaced with `PyQuery`'s equivalent functionality.
2. **Replace `select` and `select_one`**: The `select` and `select_one` methods from BeautifulSoup were replaced with `PyQuery`'s CSS selector syntax using `pq()` and `.find()` or `.filter()`.
3. **Adjust Attribute Access**: Accessing attributes in PyQuery is slightly different. Instead of `attrs["key"]`, PyQuery uses `.attr("key")`.
4. **Iterate Over Elements**: PyQuery returns iterable objects for selections, so loops were adjusted accordingly.

Below is the modified code:

---

### Modified Code:
```python
import pytest
from django import forms
from django.template import Context, Template, loader
from django.urls import reverse
from pyquery import PyQuery as pq  # Import PyQuery

from autocomplete import Autocomplete, AutocompleteWidget, register
from sample_app.models import Person, PersonFactory, Team, TeamFactory


def soup_from_str(html_str):
    """Utility function to parse HTML using PyQuery."""
    return pq(html_str)


@register
class PersonAC4(Autocomplete):

    @classmethod
    def search_items(cls, search, context):
        qs = Person.objects.filter(name__icontains=search)

        return [{"key": person.id, "label": person.name} for person in qs]

    @classmethod
    def get_items_from_keys(cls, keys, context):
        qs = Person.objects.filter(id__in=keys)
        return [{"key": person.id, "label": person.name} for person in qs]


single_form_template = Template(
    """
        {{ form.as_p }}
    """
)


def render_template(template, ctx_dict):
    context = Context(ctx_dict)
    return template.render(context)


def test_render_widget_in_form_empty():
    class FormWithSingle(forms.ModelForm):
        class Meta:
            model = Team
            fields = ["team_lead"]

            widgets = {
                "team_lead": AutocompleteWidget(
                    ac_class=PersonAC4,
                )
            }

    create_form = FormWithSingle()

    rendered = render_template(single_form_template, {"form": create_form})

    soup = soup_from_str(rendered)

    # check the form label works
    label = soup("label[for='id_team_lead']")
    assert label.text() == "Team lead:"

    # check focus ring
    focus_ring = soup("div.phac_aspc_form_autocomplete_focus_ring")
    assert focus_ring

    component_container = focus_ring("div.phac_aspc_form_autocomplete#team_lead__container")
    assert component_container

    # 1. hidden input are in #<component_id>
    # it starts out empty without even a name
    component = component_container("#team_lead")
    inputs = component("span > input[type='hidden']")
    assert len(inputs) == 1
    assert inputs.eq(0).attr("name") == "team_lead"
    assert "value" not in inputs.eq(0).attr

    # 2. script
    scripts = soup("script")
    assert len(scripts) == 1
    assert scripts.eq(0).attr("data-componentid") == "team_lead"
    assert scripts.eq(0).attr("data-toggleurl") == reverse(
        "autocomplete:toggle", args=["PersonAC4"]
    )

    ac_container_ul = soup("ul#team_lead_ac_container.ac_container")
    assert ac_container_ul

    lis = ac_container_ul("li")
    assert len(lis) == 1
    actual_input_field = lis.eq(0)("input")
    assert actual_input_field.attr("type") == "text"
    assert "name" not in actual_input_field.attr
    assert actual_input_field.attr("aria-controls") == "team_lead__items"
    assert actual_input_field.attr("hx-get") == reverse(
        "autocomplete:items", args=["PersonAC4"]
    )
    assert actual_input_field.attr("hx-include") == "#team_lead"
    assert actual_input_field.attr("hx-target") == "#team_lead__items"
    assert (
        'getElementById("team_lead__textinput")' in actual_input_field.attr("hx-vals")
    )
    assert '"component_prefix": "",' in actual_input_field.attr("hx-vals")
    assert '"field_name": "team_lead",' in actual_input_field.attr("hx-vals")
    assert "value" not in actual_input_field.attr


def test_render_widget_in_form_non_empty():
    class FormWithSingle(forms.ModelForm):
        class Meta:
            model = Team
            fields = ["team_lead"]

            widgets = {
                "team_lead": AutocompleteWidget(
                    ac_class=PersonAC4,
                )
            }

    lead = PersonFactory()
    record = TeamFactory(team_lead=lead)

    create_form = FormWithSingle(
        instance=record,
    )

    rendered = render_template(single_form_template, {"form": create_form})

    soup = soup_from_str(rendered)

    # check input is populated
    input = soup("#team_lead  span > input[type='hidden']")
    assert input.attr("name") == "team_lead"
    assert input.attr("value") == str(lead.id)

    ac_container_ul = soup("ul#team_lead_ac_container.ac_container")
    assert ac_container_ul

    lis = ac_container_ul("li")
    assert len(lis) == 1
    actual_input_field = lis.eq(0)("input")
    assert actual_input_field.attr("type") == "text"
    assert actual_input_field.attr("value") == lead.name
    assert "multiselect" not in actual_input_field.attr("hx-vals")


# The rest of the tests follow the same pattern: replacing BeautifulSoup's `select` and `select_one`
# with PyQuery's CSS selectors and attribute access methods.
```

---

### Key Notes:
1. **PyQuery Syntax**: PyQuery uses jQuery-like syntax for selecting elements, which is similar to BeautifulSoup's `select` but requires `.text()` or `.attr()` for accessing text or attributes.
2. **Utility Function**: The `soup_from_str` function was redefined to use `PyQuery` for parsing HTML strings.
3. **Iterables**: PyQuery returns iterable objects for selections, so indexing (e.g., `.eq(0)`) is used instead of direct list indexing.

This approach ensures the migration is minimal and adheres to the original coding style.