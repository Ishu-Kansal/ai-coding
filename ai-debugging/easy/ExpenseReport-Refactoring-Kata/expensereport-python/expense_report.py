# Expense report module.
# Business context: formats an expense list for a printed report, totals all
# expenses, tracks meal spend, and marks meals that exceed policy limits.
import locale
from enum import Enum, unique, auto
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from typing import List


# ExpenseType enumerates the supported business expense categories.
# Truth table:
# | type value       | expense category |
# | DINNER           | Meal             |
# | BREAKFAST        | Meal             |
# | LUNCH            | Meal             |
# | CAR_RENTAL       | Transport        |
@unique
class ExpenseType(Enum):
    DINNER = auto()
    BREAKFAST = auto()
    LUNCH = auto()
    CAR_RENTAL = auto()


_EXPENSE_DETAILS: dict[ExpenseType, tuple[str, int | None, bool]] = {
    ExpenseType.DINNER: ("Dinner", 5000, True),
    ExpenseType.BREAKFAST: ("Breakfast", 1000, True),
    ExpenseType.LUNCH: ("Lunch", 2000, True),
    ExpenseType.CAR_RENTAL: ("Car Rental", None, False),
}


# Expense is the report input record.
# Business fields: type identifies the category and amount stores the expense
# value in the smallest currency unit used by the report.
class Expense:
    type: ExpenseType
    amount: int
    currency: str = "USD"


def convert(amount: int, conversion_factor: Decimal | float) -> int:
    return int(
        (Decimal(amount) * Decimal(str(conversion_factor))).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_EVEN,
        )
    )


class ExpenseReport:
    # print_report formats and prints the complete expense report.
    # Logic truth table:
    # | expense type | amount condition | meal spend | display name | marker |
    # | DINNER       | > 5000          | Added       | Dinner       | X      |
    # | DINNER       | <= 5000         | Added       | Dinner       | blank  |
    # | BREAKFAST    | > 1000          | Added       | Breakfast    | X      |
    # | BREAKFAST    | <= 1000         | Added       | Breakfast    | blank  |
    # | LUNCH        | > 2000          | Added       | Lunch        | X      |
    # | LUNCH        | <= 2000         | Added       | Lunch        | blank  |
    # | CAR_RENTAL   | Any             | Not added   | Car Rental   | blank  |
    # | Other/unknown| Any             | Not added   | blank        | blank  |
    # Every expense, regardless of category, contributes its amount to the total.
    def print_report(
        self,
        expenses: List[Expense],
        exchange_rates: dict[str, Decimal | float] | None = None,
    ):
        # Initial report totals: no meal spend and no overall spend have occurred.
        total = 0
        meals = 0

        # Print a report heading containing the current localized date and time.
        print("Expense Report", datetime.now().strftime(locale.nl_langinfo(locale.D_T_FMT)))

        # Process each expense independently and update meal and overall totals.
        for expense in expenses:
            amount = expense.amount
            if expense.currency != "USD":
                if exchange_rates is None or expense.currency not in exchange_rates:
                    raise ValueError(f"Unsupported currency: {expense.currency}")

                amount = convert(amount, exchange_rates[expense.currency])

            name, threshold, is_meal = _EXPENSE_DETAILS[expense.type]

            if is_meal:
                meals += amount

            meal_over_expenses_marker = (
                "X" if threshold is not None and amount > threshold else " "
            )
            # Print category, amount, and policy marker for this expense row.
            print(name, "\t", amount, "\t", meal_over_expenses_marker)
            # Total includes every expense row.
            total += amount

        # Print the meal subtotal and the grand total after all rows are processed.
        print("Meals:", meals)
        print("Total:", total)
