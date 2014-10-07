# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)
import pyxb_123.binding.generate

import os.path
schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schemas/test-simplerange.xsd'))
code = pyxb_123.binding.generate.GeneratePython(schema_location=schema_path)
rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb_123.exceptions_ import *

import unittest

class TestKML (unittest.TestCase):
    def testAngle360 (self):
        self.assertEqual(25.4, angle360(25.4))
        self.assertRaises(SimpleTypeValueError, angle360, 420.0)
        self.assertRaises(SimpleTypeValueError, angle360, -361.0)

if __name__ == '__main__':
    unittest.main()

