"""Flask HTTP layer and lift-pass pricing entry point.

The module owns the app, lazy database connection, GET/PUT routes, and all
current pricing rules. It is the composition and transport boundary for this kata.
"""

import math

from flask import Flask
from flask import request
from datetime import datetime
from db import create_lift_pass_db_connection

app = Flask("lift-pass-pricing")

connection_options = {
    "host": 'localhost',
    "user": 'root',
    "database": 'lift_pass',
    "password": 'mysql'}

connection = None


def calculate_cost_for_member(pass_type, base_price, age, date=None, is_holiday=False):
    """Calculate the pass cost for one person.

    Reads:
        The pass type, base database price, age, optional date, and whether the
        date is a holiday.
    Modifies:
        None.
    Returns:
        The cost as an integer for the supplied member.
    Business logic:
        Applies age and type rules, plus the non-holiday Monday 35% discount
        for 1jour passes held by members aged 15 or older.
    """
    if pass_type not in ("night", "1jour"):
        raise ValueError("Pass type must be 'night' or '1jour'")

    if age is not None and age < 6:
        return 0

    if pass_type == "night":
        if age is None or age < 15:
            return 0
        if age <= 64:
            return base_price
        return math.ceil(base_price * .4)
    else:
        if age is not None and age < 15:
            return math.ceil(base_price * .7)

        if age is not None and age > 64:
            reduction = 35 if date is not None and not is_holiday and date.weekday() == 0 else 0
            return math.ceil(base_price * .75 * (1 - reduction / 100))

        reduction = 35 if date is not None and not is_holiday and date.weekday() == 0 else 0
        return math.ceil(base_price * (1 - reduction / 100))



@app.teardown_appcontext
def shutdown(exception=None):
    """Release the process-global database connection after a Flask context ends.

    Reads:
        The module-level connection value and optional teardown exception.
    Modifies:
        Closes a live connection and resets the module-level connection to None.
    Returns:
        None.
    Business logic:
        Ensures later requests lazily create a fresh connection when needed.
    """
    global connection
    if connection is not None:
        connection.close()
        connection = None

@app.route("/prices", methods=['GET', 'PUT'])
def prices():
    """Handle lift-pass base-price updates and price calculations.

    Reads:
        The HTTP method and query parameters (type, cost, age, and date), the
        in-memory database connection, base prices, and holiday rows.
    Modifies:
        Lazily initializes the database; PUT may replace a base-price row.
        Does not mutate other application state or the holiday table.
    Returns:
        An empty JSON-compatible object for PUT, or ``{"cost": price}`` for GET.
    Business logic:
        Under 6 is free; night passes are free under 6 and receive special senior
        pricing; day passes discount children and seniors and offer a Monday
        discount outside holiday dates. Groups of four or more paying members
        receive an additional 10% discount on non-holiday dates.
    """
    res = {}

    global connection
    if connection is None:
        connection = create_lift_pass_db_connection(connection_options)

    if request.method == 'PUT':
        lift_pass_cost = request.args["cost"]
        lift_pass_type = request.args["type"]
        cursor = connection.cursor()
        cursor.execute('REPLACE INTO `base_price` (type, cost) VALUES (?, ?)', # sqlite fix
            (lift_pass_type, lift_pass_cost))
        return {}

    elif request.method == 'GET':
        cursor = connection.cursor()
        cursor.execute(f'SELECT cost FROM base_price '
                       + 'WHERE type = ? ',
                       (request.args['type'],))
        row = cursor.fetchone()
        result = {"cost": row[0]}

        ages = request.args.getlist('age', type=int)
        age = ages if len(ages) > 1 else (ages[0] if ages else None)
        date = datetime.fromisoformat(request.args["date"]) if "date" in request.args else None

        is_holiday = False
        if date is not None:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM holidays')
            for row in cursor.fetchall():
                holiday = row[0]
                if isinstance(holiday, str):
                    holiday = datetime.fromisoformat(holiday)  # sqlite fix
                if date.year == holiday.year and date.month == holiday.month and date.day == holiday.day:
                    is_holiday = True
                    break

        if isinstance(age, list):
            member_costs = []
            paying_members = 0
            for member_age in age:
                member_cost = calculate_cost_for_member(
                    request.args["type"],
                    result["cost"],
                    member_age,
                    date,
                    is_holiday,
                )
                member_costs.append(member_cost)
                if member_cost > 0:
                    paying_members += 1

            if paying_members >= 4 and not is_holiday:
                member_costs = [
                    math.ceil(member_cost * .9) if member_cost > 0 else 0
                    for member_cost in member_costs
                ]

            res["cost"] = sum(member_costs)
        else:
            res["cost"] = calculate_cost_for_member(
                request.args["type"],
                result["cost"],
                age,
                date,
                is_holiday,
            )

    return res
