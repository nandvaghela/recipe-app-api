# Sample Test

from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):
    def test_add_numbers(self):
        res = calc.add(15, 6)

        self.assertEqual(res, 21)

    def test_subtract_numbers(self):
        res = calc.subtract(15, 9)

        self.assertEqual(res, 6)
