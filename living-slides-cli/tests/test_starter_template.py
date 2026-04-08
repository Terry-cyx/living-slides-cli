"""Tests for the C6 starter template + deprecation of presentation/business/tech."""

from __future__ import annotations

import re
import warnings

import pytest
from click.testing import CliRunner

from living_slides.cli import main
from living_slides.templates import get_template, list_templates


def test_starter_listed():
    names = {t["name"] for t in list_templates()}
    assert "starter" in names


def test_starter_has_data_oid_on_every_meaningful_element():
    html = get_template("starter", "My Deck")
    # Every <section>, <h1>, <h2>, <p>, <ul>, <li>, <div class=metric> should carry an oid.
    expected_tags = ["section", "h1", "h2", "p", "ul", "li"]
    for tag in expected_tags:
        opens = re.findall(rf"<{tag}\b[^>]*>", html)
        assert opens, f"no <{tag}> found at all"
        for open_tag in opens:
            assert "data-oid=" in open_tag, f"<{tag}> missing data-oid: {open_tag}"


def test_starter_oids_are_unique():
    html = get_template("starter", "X")
    oids = re.findall(r'data-oid="([^"]+)"', html)
    assert len(oids) == len(set(oids)), f"duplicate oids: {oids}"


def test_starter_has_four_slides():
    html = get_template("starter", "X")
    sections = re.findall(r'<section\b[^>]*class="slide"', html)
    assert len(sections) == 4


def test_starter_via_cli(tmp_path):
    f = tmp_path / "deck.html"
    result = CliRunner().invoke(main, ["create", str(f), "--template", "starter"])
    assert result.exit_code == 0, result.output
    content = f.read_text(encoding="utf-8")
    assert "data-oid" in content
    assert content.count('class="slide"') == 4


@pytest.mark.parametrize("name", ["presentation", "business", "tech"])
def test_deprecated_templates_emit_warning(name):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        get_template(name, "X")
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert deprecations, f"{name} should emit a DeprecationWarning"
    assert "v0.3" in str(deprecations[0].message)


def test_deprecated_templates_still_produce_output():
    # The grace-period contract: deprecated templates still work.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        html = get_template("presentation", "X")
    assert "<html" in html.lower()
