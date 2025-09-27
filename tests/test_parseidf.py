import unittest

from parseidf import parse


class TestParseIDF(unittest.TestCase):

    def test_single_object_no_values(self):
        idf = "Version;"
        expected = {"VERSION": [["Version"]]}
        self.assertEqual(parse(idf), expected)

    def test_single_object_with_values(self):
        idf = "Material, Brick, 0.5, 0.8;"
        expected = {"MATERIAL": [["Material", "Brick", "0.5", "0.8"]]}
        self.assertEqual(parse(idf), expected)

    def test_multiple_objects_same_type(self):
        idf = "Zone, LivingRoom, 20;\nZone, Kitchen, 15;"
        expected = {"ZONE": [["Zone", "LivingRoom", "20"], ["Zone", "Kitchen", "15"]]}
        self.assertEqual(parse(idf), expected)

    def test_multiple_objects_different_types(self):
        idf = "Building, MyHouse;\nZone, Bedroom, 12;"
        expected = {
            "BUILDING": [["Building", "MyHouse"]],
            "ZONE": [["Zone", "Bedroom", "12"]],
        }
        self.assertEqual(parse(idf), expected)

    def test_comments_are_ignored(self):
        idf = "! This is a comment\nMaterial, Wood, 0.3, 0.6; ! Another comment"
        expected = {"MATERIAL": [["Material", "Wood", "0.3", "0.6"]]}
        self.assertEqual(parse(idf), expected)

    def test_whitespace_and_newlines(self):
        idf = "  Material ,  Wood , 0.3 , 0.6 ;\n\nZone , Bedroom , 12 ;"
        expected = {
            "MATERIAL": [["Material", "Wood", "0.3", "0.6"]],
            "ZONE": [["Zone", "Bedroom", "12"]],
        }
        self.assertEqual(parse(idf), expected)

    def test_object_with_asterisk(self):
        idf = "Schedule, *, *, *;"
        expected = {"SCHEDULE": [["Schedule", "*", "*", "*"]]}
        self.assertEqual(parse(idf), expected)

    def test_syntax_error_missing_semicolon(self):
        idf = "Material, Brick, 0.5, 0.8"
        with self.assertRaises(SyntaxError):
            parse(idf)

    def test_illegal_character(self):
        idf = "Material, Brick, 0.5, 0.8; $"
        with self.assertRaises(SyntaxError):
            parse(idf)

    def test_empty_input(self):
        idf = ""
        with self.assertRaises(SyntaxError):
            parse(idf)

    def test_object_with_only_name_and_semicolon(self):
        idf = "Building;"
        expected = {"BUILDING": [["Building"]]}
        self.assertEqual(parse(idf), expected)
