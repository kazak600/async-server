import unittest


class MainTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super(MainTestCase, self).setUp()

    def tearDown(self) -> None:
        super(MainTestCase, self).tearDown()

    def test_main(self):
        self.assertEqual(True, False)
