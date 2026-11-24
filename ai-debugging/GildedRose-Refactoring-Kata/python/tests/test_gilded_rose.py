# -*- coding: utf-8 -*-
import unittest

from gilded_rose import Item, GildedRose


class GildedRoseTest(unittest.TestCase):
    def test_foo(self):
        items = [Item("foo", 0, 0)]
        gilded_rose = GildedRose(items)
        gilded_rose.update_quality()
        self.assertEqual("foo", items[0].name)
        
    def test_aged_brie_increases_for_five_updates(self):
        items = [Item("Aged Brie", 2, 46)]
        gilded_rose = GildedRose(items)

        for _ in range(5):
            gilded_rose.update_quality()

        self.assertEqual(50, items[0].quality)
        self.assertEqual(-3, items[0].sell_in)

    def test_sulfuras_remains_unchanged(self):
        items = [Item("Sulfuras, Hand of Ragnaros", 2, 80)]
        gilded_rose = GildedRose(items)

        gilded_rose.update_quality()

        self.assertEqual(80, items[0].quality)
        self.assertEqual(2, items[0].sell_in)

    def test_backstage_passes_until_sellin_is_negative_three(self):
        items = [
            Item(
                "Backstage passes to a TAFKAL80ETC concert",
                20,
                30,
            )
        ]
        gilded_rose = GildedRose(items)

        while items[0].sell_in > -3:
            gilded_rose.update_quality()

        self.assertEqual(0, items[0].quality)
        self.assertEqual(-3, items[0].sell_in)
        
    def test_approximate_aged_brie_name_is_case_insensitive(self):
        items = [Item("Blue French AGED BRIE", 2, 46)]
        gilded_rose = GildedRose(items)

        for _ in range(5):
            gilded_rose.update_quality()

        self.assertEqual(50, items[0].quality)
        self.assertEqual(-3, items[0].sell_in)

    def test_approximate_sulfuras_name_is_case_insensitive(self):
        items = [Item("SULFURAS Optimum", 2, 80)]
        gilded_rose = GildedRose(items)

        gilded_rose.update_quality()

        self.assertEqual(80, items[0].quality)
        self.assertEqual(2, items[0].sell_in)

    def test_approximate_backstage_passes_name_is_case_insensitive(self):
        items = [Item("BACKSTAGE PASSES to Skrillex", 20, 30)]
        gilded_rose = GildedRose(items)

        while items[0].sell_in > -3:
            gilded_rose.update_quality()

        self.assertEqual(0, items[0].quality)
        self.assertEqual(-3, items[0].sell_in)
    
    def test_standard_item_quality_never_goes_negative(self):
        items = [Item("Standard Item", 2, 1)]
        gilded_rose = GildedRose(items)

        gilded_rose.update_quality()
        gilded_rose.update_quality()

        self.assertGreaterEqual(items[0].quality, 0)

    def test_backstage_pass_quality_never_goes_negative(self):
        items = [Item("Backstage passes to a concert", 0, 1)]
        gilded_rose = GildedRose(items)

        gilded_rose.update_quality()

        self.assertGreaterEqual(items[0].quality, 0)

    def test_conjured_item_quality_never_goes_negative(self):
        items = [Item("Conjured Mana Cake", 2, 1)]
        gilded_rose = GildedRose(items)

        gilded_rose.update_quality()
        gilded_rose.update_quality()

        self.assertGreaterEqual(items[0].quality, 0)
        
    def test_conjured_quality_degrades_twice_as_fast(self):
        items = [Item("Conjured Mana Cake", 10, 10)]
        gilded_rose = GildedRose(items)

        for _ in range(3):
            gilded_rose.update_quality()

        self.assertEqual(4, items[0].quality)

        for _ in range(3):
            gilded_rose.update_quality()

        self.assertEqual(0, items[0].quality)
if __name__ == '__main__':
    unittest.main()
