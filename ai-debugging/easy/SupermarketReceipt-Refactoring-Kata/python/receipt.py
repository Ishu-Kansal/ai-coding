
from decimal import Decimal, ROUND_HALF_UP


class ReceiptItem:
    # Input: product, quantity, unit price, and total price; Output: initialized ReceiptItem; stores one purchased line item.
    def __init__(self, product, quantity, price, total_price):
        self.product = product
        self.quantity = quantity
        self.price = price
        self.total_price = total_price


class Receipt:
    # Input: none; Output: initialized Receipt; creates empty item and discount collections.
    def __init__(self):
        self._items = []
        self._discounts = []

    # Input: none; Output: nonnegative total rounded to cents; sums item totals and discounts.
    def total_price(self):
        total = Decimal("0.00")
        for item in self.items:
            total += Decimal(str(item.total_price))
        for discount in self.discounts:
            total += Decimal(str(discount.discount_amount))
        total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return float(max(Decimal("0.00"), total))

    # Input: product, quantity, unit price, and total price; Output: none; appends a new receipt item.
    def add_product(self, product, quantity, price, total_price):
        self._items.append(ReceiptItem(product, quantity, price, total_price))

    # Input: Discount; Output: none; appends the discount to the receipt.
    def add_discount(self, discount):
        self._discounts.append(discount)

    # Input: none; Output: copy of the receipt items; provides read access to purchased line items.
    @property
    def items(self):
        return self._items[:]

    # Input: none; Output: copy of the receipt discounts; provides read access to applied discounts.
    @property
    def discounts(self):
        return self._discounts[:]
