from django.test import TestCase
from app.calc import add, substract

class CalcTest(TestCase):

    def test_add(self):
        """ Test that two numbers are added together """
        self.assertEqual(add(3, 8), 11)
    
    def test_subtracting(self):
        """ Test that values are substracting and return """
        self.assertEqual(substract(5, 11), -6)