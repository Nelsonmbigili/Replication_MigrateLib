import json

from django.http import QueryDict
from django.urls import reverse

from autocomplete.core import Autocomplete, register
from sample_app.models import Person, PersonFactory, Team, TeamFactory

from .utils_for_test import get_pyquery  # Assuming this function returns a PyQuery object


class PersonAC3(Autocomplete):

    @classmethod
    def search_items(cls, search, context):
        qs = Person.objects.filter(name__icontains=search)

        return [{"key": person.id, "label": person.name} for person in qs]

    @classmethod
    def get_items_from_keys(cls, keys, context):
        qs = Person.objects.filter(id__in=keys)
        return [{"key": person.id, "label": person.name} for person in qs]


register(PersonAC3)


def test_toggle_response_select_from_empty_non_multi(client):
    """
    first, try adding selectin a person when none is selected
    """
    people = PersonFactory.create_batch(5)
    to_add = PersonFactory()

    base_url = reverse("autocomplete:toggle", kwargs={"ac_name": "PersonAC3"})
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "item": to_add.id,
        }
    )

    response = client.get(f"{base_url}?{qs_dict.urlencode()}")
    assert response.status_code == 200

    pyquery = get_pyquery(response)  # Changed to use PyQuery

    # 1. The element we are toggling (not sure why this is even included)
    toggled_option = pyquery("a[role='option']")
    assert len(toggled_option) == 1

    # 2. The hidden inputs that actually hold the form values
    hidden_inputs_container = pyquery("div#component_namemyfield_name")
    assert hidden_inputs_container.attr("hx-swap-oob") == "true"
    hidden_inputs = hidden_inputs_container("input[type='hidden'][name='myfield_name']")
    assert len(hidden_inputs) == 1
    assert hidden_inputs.attr("value") == str(to_add.id)

    # 3. The autocomplete input
    # this component should have mostly been tested in the items test
    text_input = pyquery("input#component_namemyfield_name__textinput")
    assert text_input.attr("hx-vals")
    assert "multiselect" not in text_input.attr("hx-vals")

    assert text_input.attr("value") == to_add.name

    # 4. The "data" span, not sure how this is used
    data_span = pyquery("span#component_namemyfield_name__data")
    assert data_span.attr("data-phac-aspc-autocomplete") == str(to_add.name)

    # 5. some script tag to keep events updated,
    script_tag = pyquery("script[data-componentid='component_namemyfield_name']")
    assert "phac_aspc_autocomplete_trigger_change" in script_tag.text()


def test_toggle_response_unselect_non_multi(client):
    """
    try toggling off a person that was selected
    """
    people = PersonFactory.create_batch(5)
    to_remove = PersonFactory()

    base_url = reverse("autocomplete:toggle", kwargs={"ac_name": "PersonAC3"})

    # next, try removign a person from a list with one person
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "myfield_name": to_remove.id,
            "component_prefix": "component_name",
            "item": to_remove.id,
        }
    )

    response = client.get(f"{base_url}?{qs_dict.urlencode()}")
    assert response.status_code == 200

    pyquery = get_pyquery(response)  # Changed to use PyQuery


def test_toggle_multi(client):
    people = PersonFactory.create_batch(5)
    p1 = PersonFactory()
    p2 = PersonFactory()

    base_url = reverse("autocomplete:toggle", kwargs={"ac_name": "PersonAC3"})
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "item": p1.id,
            "multiselect": True,
        }
    )

    response = client.get(f"{base_url}?{qs_dict.urlencode()}")
    assert response.status_code == 200

    pyquery = get_pyquery(response)  # Changed to use PyQuery

    # 1. The element we are toggling
    toggled_option = pyquery("a[role='option']")
    assert len(toggled_option) == 1

    # 2. hidden inputs
    hidden_inputs_container = pyquery("div#component_namemyfield_name")
    assert hidden_inputs_container.attr("hx-swap-oob") == "true"
    hidden_inputs = hidden_inputs_container("input[type='hidden'][name='myfield_name']")

    # 3. The autocomplete input
    assert pyquery("ul#component_namemyfield_name_ac_container")
    chips = pyquery("ul#component_namemyfield_name_ac_container > li.chip")
    chip_buttons = pyquery("ul#component_namemyfield_name_ac_container > li.chip > a")
    for chip_a in chip_buttons:
        assert "multiselect" in chip_a.attr("hx-params")
        assert "multiselect" in chip_a.attr("hx-vals")

    input_li = pyquery("ul#component_namemyfield_name_ac_container > li.input:not(.chip)")
    assert len(chips) == 1
    assert len(input_li) == 1

    # 4. The "info", I think this is a11y stuff
    info_text = pyquery("div#component_namemyfield_name__info").text()
    assert p1.name in info_text

    # 5. screen reader description, kinda redundant with 4
    sr_description = pyquery("div#component_namemyfield_name__sr_description").text()
    assert p1.name in sr_description

    assert len(hidden_inputs) == 1
    values = {int(i.attr("value")) for i in hidden_inputs}
    assert values == {p1.id}

    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "multiselect": True,
            "myfield_name": p1.id,
            "item": p2.id,
        }
    )
    response = client.get(f"{base_url}?{qs_dict.urlencode()}")
    assert response.status_code == 200

    pyquery = get_pyquery(response)  # Changed to use PyQuery

    # hidden inputs:
    hidden_inputs = pyquery("div#component_namemyfield_name input[type='hidden'][name='myfield_name']")
    assert len(hidden_inputs) == 2
    values = {int(i.attr("value")) for i in hidden_inputs}
    assert values == {p1.id, p2.id}


def test_toggle_multi_untoggle(client):
    people = PersonFactory.create_batch(5)
    p1 = PersonFactory()
    p2 = PersonFactory()
    p3 = PersonFactory()

    base_url = reverse("autocomplete:toggle", kwargs={"ac_name": "PersonAC3"})

    # untoggle from a list of 3
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "item": p1.id,
            "multiselect": True,
        }
    )
    qs_dict.setlist("myfield_name", [p1.id, p2.id, p3.id])

    response = client.get(f"{base_url}?{qs_dict.urlencode()}")
    assert response.status_code == 200

    pyquery = get_pyquery(response)  # Changed to use PyQuery

    # 1. The element we are toggling
    toggled_option = pyquery("a[role='option']")
    assert len(toggled_option) == 1

    # 2. hidden inputs
    hidden_inputs = pyquery("div#component_namemyfield_name input[type='hidden'][name='myfield_name']")
    assert len(hidden_inputs) == 2
    values = {int(i.attr("value")) for i in hidden_inputs}
    assert values == {p2.id, p3.id}

    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "item": p1.id,
            "multiselect": True,
            "myfield_name": p1.id,
        }
    )
    resp = client.get(f"{base_url}?{qs_dict.urlencode()}")
    assert resp.status_code == 200
    pyquery = get_pyquery(resp)  # Changed to use PyQuery

    hidden_inputs = pyquery("div#component_namemyfield_name input[type='hidden'][name='myfield_name']")
    assert len(hidden_inputs) == 0
