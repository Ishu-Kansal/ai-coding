# -*- coding: utf-8 -*-

class GildedRose(object):

    def __init__(self, items):
        self.items = items

    def update_quality(self):
       for item in self.items:
            normalized_name = item.name.lower()
            is_aged_brie = "aged brie" in normalized_name
            is_sulfuras = "sulfuras" in normalized_name
            is_backstage_passes = "backstage passes" in normalized_name
            is_conjured = "conjured" in normalized_name

            if not is_aged_brie and not is_backstage_passes:
                if item.quality > 0 and not is_sulfuras:
                    degradation = 2 if is_conjured else 1
                    item.quality = max(0, item.quality - degradation)
            else:
                if item.quality < 50:
                    item.quality += 1
                    if is_backstage_passes:
                        if item.sell_in < 11 and item.quality < 50:
                            item.quality += 1
                        if item.sell_in < 6 and item.quality < 50:
                            item.quality += 1

            if not is_sulfuras:
                item.sell_in -= 1

            if item.sell_in < 0:
                if is_aged_brie:
                    if item.quality < 50:
                        item.quality += 1
                elif is_backstage_passes:
                    item.quality = 0
                elif item.quality > 0 and not is_sulfuras:
                    degradation = 2 if is_conjured else 1
                    item.quality = max(0, item.quality - degradation)


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
