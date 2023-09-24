import NGUIdle
import unittest


class TestNGUIdle_cooking(unittest.TestCase):
    def setUp(self):
        self.ngu = NGUIdle.NGUIdle()

    def test_get_percentage_value(self):
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7,2%"),  7.2)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7,24%"), 7.24)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7,249"), 7.249)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+100%"),  100)


if __name__ == '__main__':
    unittest.main()
