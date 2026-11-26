import multiprocessing

import pytest
import requests
from datetime import datetime
import time

from prices import app, calculate_cost_for_member

TEST_PORT = 3006


def server(port):
    app.run(port=port)


def wait_for_server_to_start(server_url):
    started = False
    while not started:
        try:
            requests.get(server_url)
            started = True
        except Exception as e:
            time.sleep(0.2)


@pytest.fixture(autouse=True, scope="session")
def lift_pass_pricing_app():
    """ starts the lift pass pricing flask app running on localhost """
    p = multiprocessing.Process(target=server, args=(TEST_PORT,))
    p.start()
    server_url = f"http://127.0.0.1:{TEST_PORT}"
    wait_for_server_to_start(server_url)
    yield server_url
    p.terminate()


def test_something(lift_pass_pricing_app):
    response = requests.get(lift_pass_pricing_app + "/prices", params={'type': '1jour'})
    assert response.json() == {'cost': 35}


@pytest.mark.parametrize(
    ("pass_type", "base_price", "age", "expected"),
    [
        ("1jour", 35, 5, 0),
        ("night", 19, 5, 0),
        ("1jour", 35, 14, 25),
        ("night", 19, 14, 0),
        ("1jour", 35, 15, 35),
        ("night", 19, 15, 19),
        ("1jour", 35, 64, 35),
        ("night", 19, 64, 19),
        ("1jour", 35, 65, 27),
        ("night", 19, 65, 8),
    ],
)
def test_calculate_cost_for_member(pass_type, base_price, age, expected):
    assert calculate_cost_for_member(pass_type, base_price, age) == expected


def test_calculate_cost_for_member_applies_monday_discount():
    monday = datetime(2019, 2, 18)

    assert calculate_cost_for_member("1jour", 35, 15, monday) == 23
    assert calculate_cost_for_member("1jour", 35, 65, monday) == 18
    assert calculate_cost_for_member("1jour", 35, 15, monday, is_holiday=True) == 35


@pytest.mark.parametrize(
    ("pass_type", "date", "ages", "expected"),
    [
        ("night", "2019-02-19", [5, 14, 15, 64, 65, 30], 62),
        ("night", "2019-02-11", [5, 14, 15, 64, 65, 30], 62),
        ("night", "2019-02-18", [5, 14, 15, 64, 65, 30], 65),
        ("night", "2019-02-19", [15, 30, 65], 46),
        ("1jour", "2019-02-19", [5, 14, 15, 64, 65, 30], 144),
        ("1jour", "2019-02-11", [5, 14, 15, 64, 65, 30], 103),
        ("1jour", "2019-02-18", [5, 14, 15, 64, 65, 30], 157),
    ],
)
def test_group_pricing(lift_pass_pricing_app, pass_type, date, ages, expected):
    params = [("type", pass_type), ("date", date)]
    params.extend(("age", age) for age in ages)

    response = requests.get(lift_pass_pricing_app + "/prices", params=params)

    assert response.json() == {"cost": expected}
