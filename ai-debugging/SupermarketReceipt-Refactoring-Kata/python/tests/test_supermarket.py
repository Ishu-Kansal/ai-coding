import unittest

from model_objects import Discount, Product, ProductUnit, SpecialOfferType
from receipt import Receipt
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


class SupermarketTest(unittest.TestCase):
    def test_ten_percent_discount(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 0.99)

        apples = Product("apples", ProductUnit.KILO)
        catalog.add_product(apples, 1.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(apples, 2.5)

        receipt = teller.checks_out_articles_from(cart)

        self.assertEqual(receipt.total_price(), 4.98)
        self.assertEqual([], receipt.discounts)
        self.assertEqual(1, len(receipt.items))
        receipt_item = receipt.items[0]
        self.assertEqual(apples, receipt_item.product)
        self.assertEqual(1.99, receipt_item.price)
        self.assertAlmostEqual(receipt_item.total_price, 2.5 * 1.99, places=2)
        self.assertEqual(2.5, receipt_item.quantity)

    def test_total_price_does_not_drop_below_zero(self):
        product = Product("apples", ProductUnit.KILO)
        receipt = Receipt()
        receipt.add_product(product, 1, 1, 1)
        receipt.add_discount(Discount(product, "excess discount", -2))

        self.assertEqual(receipt.total_price(), 0.0)

    def test_total_price_rounds_float_drift_to_cents(self):
        product = Product("apples", ProductUnit.EACH)
        receipt = Receipt()
        receipt.add_product(product, 3, 19.99, 3 * 19.99)
        receipt.add_discount(Discount(product, "product offer", -9.97))

        self.assertEqual(receipt.total_price(), 50.00)

    def test_cart_total_offer_checks_net_subtotal_after_product_discounts(self):
        product = Product("bundle", ProductUnit.EACH)
        receipt = Receipt()
        receipt.add_product(product, 1, 52, 52)
        receipt.add_discount(Discount(product, "bundle offer", -5))

        teller = Teller(FakeCatalog())
        total = teller.cart_total_offer(receipt.total_price(), 10, 50)

        self.assertEqual(total, 47.0)

    def test_cart_total_offer_applies_at_float_drifted_threshold(self):
        teller = Teller(FakeCatalog())

        total = teller.cart_total_offer(49.99999999999999, 10, 50)

        self.assertEqual(total, 40.0)

    def test_cart_total_offer_rounds_and_never_returns_a_negative_total(self):
        teller = Teller(FakeCatalog())

        self.assertEqual(teller.cart_total_offer(60.005, 10, 50), 50.01)
        self.assertEqual(teller.cart_total_offer(5, 10, 0), 0.0)
