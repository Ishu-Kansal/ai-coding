import json
import re

import pytest
from approvaltests import verify
from approval_utilities.utils import get_adjacent_file

from statement import html_statement, statement


def test_example_statement():
    with open(get_adjacent_file("invoice.json")) as f:
        invoice = json.loads(f.read())
    with open(get_adjacent_file("plays.json")) as f:
        plays = json.loads(f.read())
    verify(statement(invoice, plays))


def test_html_statement_uses_same_figures_as_plain_text_statement():
    with open(get_adjacent_file("invoice.json")) as f:
        invoice = json.loads(f.read())
    with open(get_adjacent_file("plays.json")) as f:
        plays = json.loads(f.read())

    plain_text = statement(invoice, plays)
    html = html_statement(invoice, plays)

    assert "<h1>Statement for BigCo</h1>" in html
    assert re.findall(r"\$[\d,]+\.\d{2}", html) == re.findall(
        r"\$[\d,]+\.\d{2}", plain_text
    )
    assert re.findall(r"<td>(\d+)</td>", html) == re.findall(
        r"\((\d+) seats\)", plain_text
    )
    plain_credits = re.search(r"You earned (\d+) credits", plain_text).group(1)
    assert f"You earned <em>{plain_credits}</em> credits" in html


def test_statement_with_new_play_types():
    with open(get_adjacent_file("invoice_new_plays.json")) as f:
        invoice = json.loads(f.read())
    with open(get_adjacent_file("new_plays.json")) as f:
        plays = json.loads(f.read())
    with pytest.raises(ValueError) as exception_info:
        statement(invoice, plays)
    assert "unknown type" in str(exception_info.value)


def test_single_comedy_with_20_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "as-like", "audience": 20}
        ]
    }
    with open(get_adjacent_file("plays.json")) as f:
        plays = json.loads(f.read())

    result = statement(invoice, plays)
    assert "As You Like It: $360.00 (20 seats)" in result
    assert "Amount owed is $360.00" in result
    assert "You earned 4 credits" in result


def test_single_comedy_with_19_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "as-like", "audience": 19}
        ]
    }
    with open(get_adjacent_file("plays.json")) as f:
        plays = json.loads(f.read())

    result = statement(invoice, plays)
    assert "As You Like It: $357.00 (19 seats)" in result
    assert "Amount owed is $357.00" in result
    assert "You earned 3 credits" in result


def test_single_comedy_with_21_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "as-like", "audience": 21}
        ]
    }
    with open(get_adjacent_file("plays.json")) as f:
        plays = json.loads(f.read())

    result = statement(invoice, plays)
    assert "As You Like It: $468.00 (21 seats)" in result
    assert "Amount owed is $468.00" in result
    assert "You earned 4 credits" in result


def test_single_history_with_24_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "henry-v", "audience": 24}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"}
    }

    result = statement(invoice, plays)

    assert "Henry V: $350.00 (24 seats)" in result
    assert "Amount owed is $350.00" in result
    assert "You earned 2 credits" in result


def test_single_history_with_25_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "henry-v", "audience": 25}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"}
    }

    result = statement(invoice, plays)

    assert "Henry V: $350.00 (25 seats)" in result
    assert "Amount owed is $350.00" in result
    assert "You earned 2 credits" in result


def test_single_history_with_26_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "henry-v", "audience": 26}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"}
    }

    result = statement(invoice, plays)

    assert "Henry V: $365.00 (26 seats)" in result
    assert "Amount owed is $365.00" in result
    assert "You earned 3 credits" in result


def test_history_volume_credits_with_10_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "henry-v", "audience": 10}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"}
    }

    result = statement(invoice, plays)

    assert "You earned 1 credits" in result


def test_history_volume_credits_with_25_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "henry-v", "audience": 25}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"}
    }

    result = statement(invoice, plays)

    assert "You earned 2 credits" in result


def test_history_volume_credits_with_100_audience_members():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "henry-v", "audience": 100}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"}
    }

    result = statement(invoice, plays)

    assert "You earned 85 credits" in result


def test_history_volume_credits_double_when_history_precedes_tragedy():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "henry-v", "audience": 100},
            {"playID": "hamlet", "audience": 100}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"},
        "hamlet": {"name": "Hamlet", "type": "tragedy"}
    }

    result = statement(invoice, plays)

    assert "You earned 240 credits" in result


def test_history_volume_credits_double_when_tragedy_precedes_history():
    invoice = {
        "customer": "BigCo",
        "performances": [
            {"playID": "hamlet", "audience": 100},
            {"playID": "henry-v", "audience": 100}
        ]
    }
    plays = {
        "henry-v": {"name": "Henry V", "type": "history"},
        "hamlet": {"name": "Hamlet", "type": "tragedy"}
    }

    result = statement(invoice, plays)

    assert "You earned 240 credits" in result
