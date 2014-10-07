# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import pyxb_123
import pyxb_123.utils.utility
import pyxb_123.binding.datatypes as xsd

import unittest

class TestTrac0206 (unittest.TestCase):
    Time = "2013-08-30T11:56:45+04:00" # = 2013-08-30T07:56:45Z

    def setUp (self):
        self.__pitz = pyxb_123.PreserveInputTimeZone()
        self.__ltz = xsd.dateTime._LocalTimeZone
        xsd.dateTime._LocalTimeZone = pyxb_123.utils.utility.UTCOffsetTimeZone(120)

    def tearDown (self):
        pyxb_123.PreserveInputTimeZone(self.__pitz)
        xsd.dateTime._LocalTimeZone = self.__ltz

    def testBasic (self):
        self.assertFalse(pyxb_123.PreserveInputTimeZone())
        dt = xsd.dateTime(self.Time)
        self.assertEqual('2013-08-30 07:56:45+00:00', str(dt))
        self.assertEqual('2013-08-30 09:56:45+02:00', str(dt.aslocal()))

    def testPreserve (self):
        pyxb_123.PreserveInputTimeZone(True)
        self.assertTrue(pyxb_123.PreserveInputTimeZone())
        dt = xsd.dateTime(self.Time)
        self.assertEqual('2013-08-30 11:56:45+04:00', str(dt))
        self.assertEqual('2013-08-30 09:56:45+02:00', str(dt.aslocal()))

if __name__ == '__main__':
    unittest.main()
