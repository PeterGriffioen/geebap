#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import ee
from .. import satcol, scores
from geetools import tools
import json
import math

ee.Initialize()

class TestOuliers(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.band = "B1"
        self.p = ee.Geometry.Point(-71.5, -42.5)

        self.col = satcol.Collection.Landsat8TOA().colEE
        self.col = self.col.filterBounds(self.p).filterDate("2016-11-15", "2017-03-15")

        # TEST: MASK VALUES LESS THAN 0.11 ##
        def mask(img):
            m = img.select(self.band).lte(0.11)
            return img.updateMask(m.Not())
        self.col = self.col.map(mask).map(tools.mask2zero)
        ##############

    def test_median(self):
        '''
        # SECTION TO GENERATE THE RESULT TO COMPARE
        def listval(band):
            def wrap(img, it):
                val = img.reduceRegion(ee.Reducer.first(), self.p, 30).get(band)
                return ee.List(it).add(ee.Number(val))
            return wrap

        list = self.col.iterate(listval(self.band), ee.List([]))

        # Sort list of values
        list = ee.List(list).sort()

        # self.assertEqual(list.getInfo(), val_list)

        # SCORE
        mean = ee.Number(list.reduce(ee.Reducer.mean()))
        std = ee.Number(list.reduce(ee.Reducer.stdDev()))

        min = mean.subtract(std)
        max = mean.add(std)

        def compute_score(el):
            el = ee.Number(el)
            cond = el.gte(min).And(el.lte(max))

            return ee.Algorithms.If(cond,
            ee.List([ee.Number(el).multiply(10000).format('%.0f'), 1]),
            ee.List([ee.Number(el).multiply(10000).format('%.0f'), 0]))

        to_compare = ee.Dictionary(ee.List(list.map(compute_score)).flatten()).getInfo()
        '''

        # OUTLIER SCORE
        score = scores.Outliers((self.band,))
        self.newcol = self.col.map(score.map(self.col))

        to_compare = {
            "1210": 1, "7579": 0, "1159": 1, "1399": 1, "1171": 1, "1240": 1,
            "1200": 1, "1132": 0, "1328": 1, "1123": 0, "1168": 1, "1150": 1,
            "1178": 1, "0": 0, "1874": 0, "1846": 1, "3090": 0, "1100": 0,
            "1341": 1, "1249": 1, "1866": 1}

        # OUTLIERS SCORE
        val_dict = tools.imagecollection.get_values(self.newcol, self.p,  scale = 30, side ='client')
        # print(json.dumps(val_dict.values(), indent=2))

        # OUTLIER SCORE
        compare = [(str(int(round(val[self.band]*10000))), val["score-outlier"]) for key, val in val_dict.items()]
        compare = dict(compare)

        self.assertDictEqual(to_compare, compare)

    def test_mean(self):
        score = scores.Outliers((self.band,), 'mean')
        self.newcol = self.col.map(score.map(self.col))

        to_compare = {
            "1210": 1, "7579": 0, "1159": 1, "1399": 1, "1171": 1, "1240": 1,
            "1200": 1, "1132": 1, "1328": 1, "1123": 1, "1168": 1, "1150": 1,
            "1178": 1, "0": 0, "1874": 1, "1846": 1, "3090": 0, "1100": 1,
            "1341": 1, "1249": 1, "1866": 1}

        # OUTLIERS SCORE
        val_dict = tools.imagecollection.get_values(self.newcol, self.p,  scale = 30, side ='client')
        # print(json.dumps(val_dict.values(), indent=2))

        # OUTLIER SCORE
        compare = [(str(int(round(val[self.band]*10000))), val[score.name]) for key, val in val_dict.items()]
        compare = dict(compare)

        self.assertDictEqual(to_compare, compare)