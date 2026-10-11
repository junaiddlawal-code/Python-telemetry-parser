import unittest
from main import parse_weight

class TestFormulationParser(unittest.TestCase):
    
    def test_parse_weight_grams(self):
        self.assertEqual(parse_weight("126g"), 126.0)
        self.assertEqual(parse_weight("500G"), 500.0)
        self.assertEqual(parse_weight(" 3.5 g "), 3.5) # Test whitespace handling
        
    def test_parse_weight_kilograms(self):
        self.assertEqual(parse_weight("0.126KG"), 126.0)
        self.assertEqual(parse_weight("1kg"), 1000.0)
        
    def test_parse_weight_invalid(self):
        with self.assertRaises(ValueError):
            parse_weight("100 LBS")

if __name__ == '__main__':
    unittest.main()