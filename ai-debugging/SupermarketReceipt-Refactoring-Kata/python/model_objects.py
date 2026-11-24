from enum import Enum


class Product:
    # Input: name and unit type; Output: initialized Product; stores the product identity and selling unit.
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit


class ProductQuantity:
    # Input: product and quantity; Output: initialized ProductQuantity; stores a purchased quantity for a product.
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity


class ProductUnit(Enum):
    EACH = 1
    KILO = 2


class SpecialOfferType(Enum):
    THREE_FOR_TWO = 1
    TEN_PERCENT_DISCOUNT = 2
    TWO_FOR_AMOUNT = 3
    FIVE_FOR_AMOUNT = 4

class Offer:
    # Input: offer type, product, and offer argument; Output: initialized Offer; stores the product discount configuration.
    def __init__(self, offer_type, product, argument):
        self.offer_type = offer_type
        self.product = product
        self.argument = argument


class Discount:
    # Input: product, description, and discount amount; Output: initialized Discount; stores a negative receipt discount.
    def __init__(self, product, description, discount_amount):
        self.product = product
        self.description = description
        self.discount_amount = discount_amount
