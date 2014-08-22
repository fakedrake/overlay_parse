try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase


class BaseTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
