import io
import sys
import pytest

from approvaltests import approvals, Options
from approvaltests.scrubbers.date_scrubber import DateScrubber

import expense_report

def createExpense(type, amount, currency="USD"):
    expense = expense_report.Expense()
    expense.type = type
    expense.amount = amount
    expense.currency = currency
    return expense

def test_expense_report():
    orig_sysout = sys.stdout
    try:
        fake_stdout = io.StringIO()
        sys.stdout = fake_stdout

        expenses = [
            createExpense(expense_report.ExpenseType.DINNER, 5000),
            createExpense(expense_report.ExpenseType.DINNER, 5001),
            createExpense(expense_report.ExpenseType.BREAKFAST, 1000),
            createExpense(expense_report.ExpenseType.BREAKFAST, 1001),
            createExpense(expense_report.ExpenseType.LUNCH, 2001),
            createExpense(expense_report.ExpenseType.CAR_RENTAL, 200)
        ]
        expense_report.ExpenseReport().print_report(expenses)

        answer = fake_stdout.getvalue()
        approvals.verify(answer, options=Options().add_scrubber(
            DateScrubber(
                r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-3]?\d (?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d \d{4}"
            ).scrub
        ))
    finally:
        sys.stdout = orig_sysout


@pytest.mark.parametrize(
    ("expense_type", "amount", "expected_marker"),
    [
        (expense_report.ExpenseType.DINNER, 5000, ""),
        (expense_report.ExpenseType.DINNER, 4000, ""),
        (expense_report.ExpenseType.DINNER, 6000, "X"),
        (expense_report.ExpenseType.BREAKFAST, 1000, ""),
        (expense_report.ExpenseType.BREAKFAST, 500, ""),
        (expense_report.ExpenseType.BREAKFAST, 1500, "X"),
        (expense_report.ExpenseType.LUNCH, 1000, ""),
        (expense_report.ExpenseType.LUNCH, 2000, ""),
        (expense_report.ExpenseType.LUNCH, 2001, "X"),
    ],
)
def test_meal_over_expenses_marker(expense_type, amount, expected_marker):
    orig_sysout = sys.stdout
    try:
        fake_stdout = io.StringIO()
        sys.stdout = fake_stdout

        expense_report.ExpenseReport().print_report([
            createExpense(expense_type, amount)
        ])

        expense_row = fake_stdout.getvalue().splitlines()[1]
        marker = expense_row.split("\t")[-1].strip()

        assert marker == expected_marker
    finally:
        sys.stdout = orig_sysout


def test_meal_over_expenses_marker_uses_converted_usd_amount():
    orig_sysout = sys.stdout
    try:
        fake_stdout = io.StringIO()
        sys.stdout = fake_stdout

        expense_report.ExpenseReport().print_report(
            [createExpense(expense_report.ExpenseType.DINNER, 6000, "JPY")],
            exchange_rates={"JPY": 0.0067},
        )

        expense_row = fake_stdout.getvalue().splitlines()[1]
        amount, marker = expense_row.split("\t")[1:]

        assert amount.strip() == "40"
        assert marker.strip() == ""
    finally:
        sys.stdout = orig_sysout


@pytest.mark.parametrize(
    ("amount", "expected_usd_amount", "expected_marker"),
    [
        (2000, 5000, ""),
        (2000.5, 5001, "X"),
    ],
)
def test_currency_rate_2_5_converts_dinner_before_checking_limit(
    amount, expected_usd_amount, expected_marker
):
    orig_sysout = sys.stdout
    try:
        fake_stdout = io.StringIO()
        sys.stdout = fake_stdout

        expense_report.ExpenseReport().print_report(
            [createExpense(expense_report.ExpenseType.DINNER, amount, "TEST")],
            exchange_rates={"TEST": 2.5},
        )

        expense_row = fake_stdout.getvalue().splitlines()[1]
        converted_amount, marker = expense_row.split("\t")[1:]

        assert int(converted_amount.strip()) == expected_usd_amount
        assert marker.strip() == expected_marker
    finally:
        sys.stdout = orig_sysout


def test_summaries_sum_rounded_converted_line_items():
    orig_sysout = sys.stdout
    try:
        fake_stdout = io.StringIO()
        sys.stdout = fake_stdout

        expenses = [
            createExpense(expense_report.ExpenseType.DINNER, 1, "HALF"),
            createExpense(expense_report.ExpenseType.BREAKFAST, 1, "HALF"),
            createExpense(expense_report.ExpenseType.CAR_RENTAL, 1, "HALF"),
        ]
        expense_report.ExpenseReport().print_report(
            expenses,
            exchange_rates={"HALF": 0.5},
        )

        lines = fake_stdout.getvalue().splitlines()
        line_amounts = [int(line.split("\t")[1].strip()) for line in lines[1:4]]
        meals = int(lines[-2].split(":")[1].strip())
        total = int(lines[-1].split(":")[1].strip())

        assert line_amounts == [0, 0, 0]
        assert meals == sum(line_amounts[:2]) == 0
        assert total == sum(line_amounts) == 0
    finally:
        sys.stdout = orig_sysout

