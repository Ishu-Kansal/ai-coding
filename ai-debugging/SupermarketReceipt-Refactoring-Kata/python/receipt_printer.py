from model_objects import ProductUnit

class ReceiptPrinter:

    # Input: optional column width; Output: initialized ReceiptPrinter; configures the receipt text width.
    def __init__(self, columns=40):
        self.columns = columns

    # Input: Receipt; Output: formatted receipt string; presents items, discounts, and the total.
    def print_receipt(self, receipt):
        result = ""
        for item in receipt.items:
            receipt_item = self.print_receipt_item(item)
            result += receipt_item

        for discount in receipt.discounts:
            discount_presentation = self.print_discount(discount)
            result += discount_presentation

        result += "\n"
        result += self.present_total(receipt)
        return str(result)

    # Input: ReceiptItem; Output: formatted item line; presents an item's name, total, and optional unit detail.
    def print_receipt_item(self, item):
        total_price_printed = self.print_price(item.total_price)
        name = item.product.name
        line = self.format_line_with_whitespace(name, total_price_printed)
        if item.quantity != 1:
            line += f"  {self.print_price(item.price)} * {self.print_quantity(item)}\n"
        return line

    # Input: name and value strings; Output: aligned line string; pads the name and appends the value.
    def format_line_with_whitespace(self, name, value):
        line = name
        whitespace_size = self.columns - len(name) - len(value)
        for i in range(whitespace_size):
            line += " "
        line += value
        line += "\n"
        return line

    # Input: numeric price; Output: formatted price string; renders the price with two decimal places.
    def print_price(self, price):
        return "%.2f" % price

    # Input: ReceiptItem; Output: formatted quantity string; renders each units as integers and weight units with three decimals.
    def print_quantity(self, item):
        if ProductUnit.EACH == item.product.unit:
            return str(item.quantity)
        else:
            return '%.3f' % item.quantity

    # Input: Discount; Output: formatted discount line; presents the discount description and amount.
    def print_discount(self, discount):
        name = f"{discount.description} ({discount.product.name})"
        value = self.print_price(discount.discount_amount)
        return self.format_line_with_whitespace(name, value)

    # Input: Receipt; Output: formatted total line; presents the receipt's final total.
    def present_total(self, receipt):
        name = "Total: "
        value = self.print_price(receipt.total_price())
        return self.format_line_with_whitespace(name, value)
