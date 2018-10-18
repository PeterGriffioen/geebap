import ee
ee.Initialize()

from geebap.tests import test_bap

thisTest = test_bap.TestBAP()
thisTest.setUp()
thisTest.test_bap2016_0()
