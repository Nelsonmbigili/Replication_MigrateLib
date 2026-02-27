import json
from pyquery import PyQuery as pq

from django.http import HttpRequest, QueryDict
from django.urls import reverse

from autocomplete.core import Autocomplete, register
from autocomplete.views import replace_or_toggle, toggle_set
from sample_app.models import Person, PersonFactory, Team, TeamFactory
from tests.conftest import PersonAC

from .utils_for_test import get_soup


def test_items_response_non_multi(client):

    people = PersonFactory.create_batch(5)
    searchable_person = PersonFactory(name="abcdefg")
    searchable_person2 = PersonFactory(name="abcdxyz")

    base_url = reverse("autocomplete:items", kwargs={"ac_name": "PersonAC"})
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "search": "abcd",
        }
    )
    full_url = f"{base_url}?{qs_dict.urlencode()}"

    response = client.get(full_url)
    assert response.status_code == 200

    soup = pq(response.content)

    listbox = soup("div[role='listbox']")
    assert listbox.attr("id") == "component_namemyfield_name__items"
    assert "aria-multiselectable" not in listbox.attr

    # abcd should match two people,
    options = listbox("a")
    assert len(options) == 2
    assert "abcdefg" in options.eq(0).text()
    assert "abcdxyz" in options.eq(1).text()

    assert json.loads(options.eq(0).attr("hx-vals")) == {
        "field_name": "myfield_name",
        "component_prefix": "component_name",
        "item": str(searchable_person.id),
    }
    assert json.loads(options.eq(1).attr("hx-vals")) == {
        "field_name": "myfield_name",
        "component_prefix": "component_name",
        "item": str(searchable_person2.id),
    }

    highlight_span = listbox("span.highlight")
    assert highlight_span.text() == "abcd"

    assert options.eq(0).attr("hx-get") == reverse(
        "autocomplete:toggle", kwargs={"ac_name": "PersonAC"}
    )
    assert (
        options.eq(0).attr("hx-params") == "myfield_name,field_name,item,component_prefix"
    )
    assert options.eq(0).attr("hx-include") == "#component_namemyfield_name"
    assert "component_namemyfield_name__item__" in options.eq(0).attr("id")
    assert not options.eq(1).attr("id") == options.eq(0).attr("id")


def test_items_response_multi(client):

    class PersonAC2(Autocomplete):
        # registry is not cleared between tests, must use unique names

        @classmethod
        def search_items(cls, search, context):
            qs = Person.objects.filter(name__icontains=search)

            return [{"key": person.id, "label": person.name} for person in qs]

        @classmethod
        def get_items_from_keys(cls, keys, context):
            return Person.objects.filter(id__in=keys)

    register(PersonAC2)

    people = PersonFactory.create_batch(5)
    searchable_person = PersonFactory(name="abcdefg")
    searchable_person2 = PersonFactory(name="abcdxyz")

    base_url = reverse("autocomplete:items", kwargs={"ac_name": "PersonAC2"})
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "search": "abcd",
            "multiselect": True,
        }
    )
    full_url = f"{base_url}?{qs_dict.urlencode()}"

    response = client.get(full_url)
    assert response.status_code == 200

    soup = pq(response.content)

    listbox = soup("div[role='listbox']")
    assert listbox.attr("id") == "component_namemyfield_name__items"
    assert listbox.attr("aria-multiselectable") == "true"
    assert listbox.attr("aria-description") == "multiselect"

    # abcd should match two people,
    options = listbox("a")
    assert len(options) == 2
    assert "abcdefg" in options.eq(0).text()
    assert "abcdxyz" in options.eq(1).text()

    assert json.loads(options.eq(0).attr("hx-vals")) == {
        "field_name": "myfield_name",
        "component_prefix": "component_name",
        "item": str(searchable_person.id),
        "multiselect": True,
    }
    assert json.loads(options.eq(1).attr("hx-vals")) == {
        "field_name": "myfield_name",
        "component_prefix": "component_name",
        "item": str(searchable_person2.id),
        "multiselect": True,
    }

    highlight_span = listbox("span.highlight")
    assert highlight_span.text() == "abcd"

    assert options.eq(0).attr("hx-get") == reverse(
        "autocomplete:toggle", kwargs={"ac_name": "PersonAC2"}
    )
    assert (
        options.eq(0).attr("hx-params")
        == "myfield_name,field_name,item,component_prefix,multiselect"
    )
    assert options.eq(0).attr("hx-include") == "#component_namemyfield_name"
    assert "component_namemyfield_name__item__" in options.eq(0).attr("id")
    assert not options.eq(1).attr("id") == options.eq(0).attr("id")

    # now add abcdefg as member and try again,
    qs_dict.setlist("myfield_name", [searchable_person.id])
    full_url = f"{base_url}?{qs_dict.urlencode()}"

    response = client.get(full_url)
    assert response.status_code == 200

    soup = pq(response.content)

    options = soup("div[role='listbox'] > a")
    assert len(options) == 2
    assert "abcdefg" in options.eq(0).text()
    assert "abcdxyz" in options.eq(1).text()

    assert options.eq(0).attr("aria-selected") == "true"
    assert options[0].attrs["aria-selected"] == "true"


def test_custom_options(client):

    people = PersonFactory.create_batch(5)
    searchable_person = PersonFactory(name="abcdefg")
    searchable_person2 = PersonFactory(name="abcdxyz")

    base_url = reverse("autocomplete:items", kwargs={"ac_name": "PersonAC"})

    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "search": "abcd",
            "placeholder": "my placeholder",
            "required": True,
            "disabled": True,
        }
    )
    full_url = f"{base_url}?{qs_dict.urlencode()}"

    response = client.get(full_url)
    assert response.status_code == 200

    soup = get_soup(response)

    result = soup.select_one("div[role='listbox'] a[role='option']")
    hx_params = result.attrs["hx-params"].split(",")
    assert "required" in hx_params
    assert "disabled" in hx_params
    assert "placeholder" in hx_params

    hx_vals = json.loads(result.attrs["hx-vals"])
    assert hx_vals["required"]
    assert hx_vals["disabled"]
    assert hx_vals["placeholder"] == "my placeholder"


def test_limit_results(client):
    people = PersonFactory.create_batch(5)
    searchable_person = PersonFactory(name="abcdefg")
    searchable_person2 = PersonFactory(name="abcdxyz")
    searchable_person3 = PersonFactory(name="abcdxyz2")

    @register
    class LimitedPersonAC(PersonAC):
        max_results = 2
        narrow_search_text = "NARROW IT DOWN"

    base_url = reverse("autocomplete:items", kwargs={"ac_name": "LimitedPersonAC"})
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield",
            "search": "abcd",
        }
    )
    full_url = f"{base_url}?{qs_dict.urlencode()}"

    response = client.get(full_url)
    assert response.status_code == 200

    soup = get_soup(response)
    listbox = soup.select_one("div[role='listbox']")
    results = listbox.select("a")
    assert len(results) == 2

    more_results = listbox.select_one("div.more-results")
    assert "NARROW IT DOWN" in more_results.get_text()


def test_no_results(client):
    @register
    class NoResultsPersonAC(PersonAC):
        max_results = 2
        no_result_text = "NO RESULTS"

    base_url = reverse("autocomplete:items", kwargs={"ac_name": "NoResultsPersonAC"})
    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield",
            "search": "abcd",
        }
    )
    full_url = f"{base_url}?{qs_dict.urlencode()}"
    response = client.get(full_url)
    assert response.status_code == 200

    soup = get_soup(response)
    listbox = soup.select_one("div[role='listbox']")
    results = listbox.select("a")
    assert len(results) == 0
    items = listbox.select("span.item")
    assert len(items) == 1
    assert "NO RESULTS" in items[0].get_text()


def test_query_too_short(client):
    base_url = reverse("autocomplete:items", kwargs={"ac_name": "PersonAC"})

    qs_dict = QueryDict(mutable=True)
    qs_dict.update(
        {
            "field_name": "myfield_name",
            "component_prefix": "component_name",
            "search": "s",
            "placeholder": "my placeholder",
            "required": True,
            "disabled": True,
        }
    )
    full_url = f"{base_url}?{qs_dict.urlencode()}"

    response = client.get(full_url)
    assert response.status_code == 200

    soup = get_soup(response)

    listbox = soup.select_one("div[role='listbox']")
    results = listbox.select("a")
    assert len(results) == 0
    items = listbox.select("span.item")
    assert len(items) == 1
    assert "Type at least 3 characters" in items[0].get_text()


def test_toggle_set():
    assert toggle_set({1, 2, "3"}, 1) == {2, "3"}

    assert toggle_set({1, 2, "3"}, "1") == {2, "3"}

    assert toggle_set({1, 2, "3"}, 3) == {1, 2}

    assert toggle_set({1, 2, "3"}, "3") == {1, 2}

    assert toggle_set({1, 2, "3"}, 4) == {1, 2, "3", 4}


def test_replace_or_toggle():

    assert replace_or_toggle({1}, 1) == set()
    assert replace_or_toggle({1}, "1") == set()
    assert replace_or_toggle({"1"}, 1) == set()
    assert replace_or_toggle({1}, 2) == {2}