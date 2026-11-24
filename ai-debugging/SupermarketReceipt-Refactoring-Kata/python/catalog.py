
class SupermarketCatalog:

    # Input: product and price; Output: none; stores or registers the catalog price for the product.
    def add_product(self, product, price):
        raise Exception("cannot be called from a unit test - it accesses the database")

    # Input: product; Output: the product's unit price; retrieves the catalog price for the product.
    def unit_price(self, product):
        raise Exception("cannot be called from a unit test - it accesses the database")

