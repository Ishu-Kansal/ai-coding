import math
from html import escape


def _format_as_dollars(amount):
    return f"${amount:0,.2f}"


def _calculate_statement(invoice, plays):
    total_amount = 0
    volume_credits = 0
    performances = []

    play_types = {
        plays[perf['playID']]['type']
        for perf in invoice['performances']
    }
    double_history_credits = {"history", "tragedy"}.issubset(play_types)

    for perf in invoice['performances']:
        play = plays[perf['playID']]
        if play['type'] == "tragedy":
            this_amount = 40000
            if perf['audience'] > 30:
                this_amount += 1000 * (perf['audience'] - 30)
        elif play['type'] == "comedy":
            this_amount = 30000
            if perf['audience'] > 20:
                this_amount += 10000 + 500 * (perf['audience'] - 20)

            this_amount += 300 * perf['audience']
        elif play['type'] == "history":
            this_amount = 35000
            if perf['audience'] > 25:
                this_amount += 1500 * (perf['audience'] - 25)

        else:
            raise ValueError(f'unknown type: {play["type"]}')

        # add volume credits
        if play["type"] == "history":
            history_credits = (
                max(perf['audience'] - 25, 0)
                + math.floor(perf['audience'] / 10)
            )
            volume_credits += history_credits * (2 if double_history_credits else 1)
        else:
            volume_credits += max(perf['audience'] - 30, 0)
        # add extra credit for every ten comedy attendees
        if "comedy" == play["type"]:
            volume_credits += math.floor(perf['audience'] / 5)

        performances.append((play["name"], perf["audience"], this_amount))
        total_amount += this_amount

    return invoice["customer"], performances, total_amount, volume_credits


def statement(invoice, plays):
    customer, performances, total_amount, volume_credits = _calculate_statement(
        invoice, plays
    )
    result = f'Statement for {customer}\n'

    for play_name, audience, amount in performances:
        result += f' {play_name}: {_format_as_dollars(amount/100)} ({audience} seats)\n'

    result += f'Amount owed is {_format_as_dollars(total_amount/100)}\n'
    result += f'You earned {volume_credits} credits\n'
    return result


def html_statement(invoice, plays):
    customer, performances, total_amount, volume_credits = _calculate_statement(
        invoice, plays
    )
    result = (
        "<html>\n"
        "<body>\n"
        f"<h1>Statement for {escape(customer)}</h1>\n"
        "<table>\n"
        "<tr><th>Play</th><th>Seats</th><th>Cost</th></tr>\n"
    )

    for play_name, audience, amount in performances:
        result += (
            f"<tr><td>{escape(play_name)}</td><td>{audience}</td>"
            f"<td>{_format_as_dollars(amount/100)}</td></tr>\n"
        )

    result += (
        "</table>\n"
        f"<p>Amount owed is <em>{_format_as_dollars(total_amount/100)}</em></p>\n"
        f"<p>You earned <em>{volume_credits}</em> credits</p>\n"
        "</body>\n"
        "</html>\n"
    )
    return result


