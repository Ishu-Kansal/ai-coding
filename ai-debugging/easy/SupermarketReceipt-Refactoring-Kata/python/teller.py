from decimal import Decimal, ROUND_HALF_UP

from model_objects import Offer
from receipt import Receipt


class Teller:

    # Input: SupermarketCatalog; Output: initialized Teller; configures catalog lookup and an empty offer mapping.
    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}

    # Input: product name; Output: matching Product; looks it up in the catalog's product dictionary.
    def product_with_name(self, name):
        return self.catalog.products[name]

    # Input: net cart total, discount, and threshold; Output: rounded nonnegative total after any qualifying discount.
    def cart_total_offer(self, total_price, discount_amount, threshold_amount):
        cents = Decimal("0.01")
        total = max(
            Decimal("0.00"),
            Decimal(str(total_price)).quantize(cents, rounding=ROUND_HALF_UP),
        )
        threshold = Decimal(str(threshold_amount)).quantize(cents, rounding=ROUND_HALF_UP)
        if total >= threshold:
            discount = Decimal(str(discount_amount)).quantize(cents, rounding=ROUND_HALF_UP)
            total = max(Decimal("0.00"), total - discount)
        return float(total)

    # Input: offer type, product, and offer argument; Output: none; registers or replaces the product's special offer.
    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = Offer(offer_type, product, argument)

    # Input: ShoppingCart; Output: Receipt; calculates line prices and applies all applicable cart offers.
    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()
        product_quantities = the_cart.items
        for pq in product_quantities:
            p = pq.product
            quantity = pq.quantity
            unit_price = self.catalog.unit_price(p)
            price = quantity * unit_price
            receipt.add_product(p, quantity, unit_price, price)

        the_cart.handle_offers(receipt, self.offers, self.catalog)

        return receipt
