"""
Start texttest from a command prompt in the same folder as this file with this command:

texttest -a sr -d .
"""

import sys,csv
from pathlib import Path

from model_objects import Product, SpecialOfferType, ProductUnit
from receipt_printer import ReceiptPrinter
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


def read_catalog(catalog_file):
    catalog = FakeCatalog()
    if not catalog_file.exists():
        return catalog
    with open(catalog_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            unit = ProductUnit[row['unit']]
            price = float(row['price'])
            product = Product(name, unit)
            catalog.add_product(product, price)
    return catalog


def read_offers(offers_file, teller):
    if not offers_file.exists():
        return
    with open(offers_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            offerType = SpecialOfferType[row['offer']]
            argument = float(row['argument'])
            product = teller.product_with_name(name)
            teller.add_special_offer(offerType, product, argument)


def read_basket(cart_file, catalog):
    cart = ShoppingCart()
    if not cart_file.exists():
        return cart
    with open(cart_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            quantity = float(row['quantity'])
            product = catalog.products[name]
            cart.add_item_quantity(product, quantity)
    return cart


def test_pineapple_two_for_ten():
    catalog = FakeCatalog()
    pineapple = Product("pineapple", ProductUnit.EACH)
    catalog.add_product(pineapple, 6)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, pineapple, 10)

    cart = ShoppingCart()
    cart.add_item_quantity(pineapple, 1)
    cart.add_item_quantity(pineapple, 2)

    receipt = teller.checks_out_articles_from(cart)
    res = ReceiptPrinter().print_receipt(receipt)
    
    assert receipt.total_price() == 16
    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == -2
    return res


def test_pear_five_for_four():
    catalog = FakeCatalog()
    pear = Product("pear", ProductUnit.EACH)
    catalog.add_product(pear, 1)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, pear, 4)

    cart = ShoppingCart()
    cart.add_item_quantity(pear, 10)

    receipt = teller.checks_out_articles_from(cart)
    assert receipt.total_price() == 8
    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == -2
    return ReceiptPrinter().print_receipt(receipt)


def test_apple_three_for_two():
    catalog = FakeCatalog()
    apple = Product("apple", ProductUnit.EACH)
    catalog.add_product(apple, 2)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, apple, 0)

    cart = ShoppingCart()
    cart.add_item_quantity(apple, 4)

    receipt = teller.checks_out_articles_from(cart)
    assert receipt.total_price() == 6
    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].discount_amount == -2
    return ReceiptPrinter().print_receipt(receipt)


def test_orange_ten_percent_discount():
    catalog = FakeCatalog()
    orange = Product("orange", ProductUnit.EACH)
    catalog.add_product(orange, 1.5)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, orange, 10)

    cart = ShoppingCart()
    cart.add_item_quantity(orange, 4)

    receipt = teller.checks_out_articles_from(cart)
    assert round(receipt.total_price(), 2) == 5.4
    assert len(receipt.discounts) == 1
    assert round(receipt.discounts[0].discount_amount, 2) == -0.6
    return ReceiptPrinter().print_receipt(receipt)


def main(args):
    if args == ["pineapple"]:
        print(test_pineapple_two_for_ten())
        return
    if args == ["pear"]:
        print(test_pear_five_for_four())
        return
    if args == ["apple"]:
        print(test_apple_three_for_two())
        return
    if args == ["orange"]:
        print(test_orange_ten_percent_discount())
        return

    catalog = read_catalog(Path("catalog.csv"))
    teller = Teller(catalog)
    read_offers(Path("offers.csv"), teller)
    basket = read_basket(Path("cart.csv"), catalog)
    receipt = teller.checks_out_articles_from(basket)
    print(ReceiptPrinter().print_receipt(receipt))


if __name__ == "__main__":
    main(sys.argv[1:])