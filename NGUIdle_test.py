import NGUIdle
import unittest


class TestNGUIdle_cooking(unittest.TestCase):
    def setUp(self):
        self.ngu = NGUIdle.NGUIdle()

    def test_get_percentage_value(self):
        self.assertEqual(self.ngu.cooking.get_percentage_value("+0%"),  0.0)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+0,1%"),  0.1)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+0,12%"),  0.12)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7%"),  7.0)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7,2%"),  7.2)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7,24%"), 7.24)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+7,249"), 7.24, delta=0.01)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+100%"),  100)

    def test_get_percentage_value_guess(self):
        self.assertEqual(self.ngu.cooking.get_percentage_value("100"),  100)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+100"),  100)
        self.assertEqual(self.ngu.cooking.get_percentage_value("100%"),  100)
        self.assertEqual(self.ngu.cooking.get_percentage_value("100%"),  100)

        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+45.56"), 45.5,  delta=0.1)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+45.52"), 45.52, delta=0.1)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+4552"),  45.52, delta=0.1)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+4556"),  45.5,  delta=0.1)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+455%"),  4.55,  delta=0.1)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+1234%"), 12.34, delta=0.0)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+123%"),  1.23,  delta=0.0)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("1234%"),  12.34, delta=0.0)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("1234"),   12.34, delta=0.1)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("012%"),   0.12, delta=0.0)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("01%"),    0.1, delta=0.0)

    def test_get_percentage_value_no_guess(self):
        self.assertEqual(self.ngu.cooking.get_percentage_value("+0%"),          0.0)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+0,1%"),        0.1)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+0,12%"),       0.12)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7%"),          7.0)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7,2%"),        7.2)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+7,24%"),       7.24)
        self.assertAlmostEqual(self.ngu.cooking.get_percentage_value("+7,249"), 7.24, delta=0.01)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+100%"),        100)
        self.assertEqual(self.ngu.cooking.get_percentage_value("100", False),   100)
        self.assertEqual(self.ngu.cooking.get_percentage_value("+100", False),  100)
        self.assertEqual(self.ngu.cooking.get_percentage_value("100%", False),  100)
        self.assertEqual(self.ngu.cooking.get_percentage_value("100%", False),  100)

        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "+45.56", False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "+45.52", False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "+4552",  False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "+4556",  False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "+455%",  False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "+1234%", False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "+123%",  False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "1234%",  False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "1234",   False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "012%",   False)
        self.assertRaises(ValueError, self.ngu.cooking.get_percentage_value, "01%",    False)


if __name__ == '__main__':
    unittest.main()
