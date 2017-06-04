from django.test import TestCase
from wordclips.utils.inputparser import InputParser


class ParserTestCase(TestCase):
    def setUp(self):
        self.parserSpace = InputParser(" ")
        self.parserDot = InputParser(".")


    def test_parser_space_delim(self):
        """
        Sentence can be corectly separated by space
        """
        wl = self.parserSpace.parse("Howareyou")
        self.assertEqual(wl, ["Howareyou"])
        wl = self.parserSpace.parse("How are you")
        self.assertEqual(wl, ["How", "are", "you"])
        wl = self.parserSpace.parse("How are   you")
        self.assertEqual(wl, ["How", "are", "", "", "you"])
        wl = self.parserSpace.parse("How are       you")
        self.assertEqual(wl, ["How", "are", "", "", "", "", "", "", "you"])


    def test_parser_default(self):
        """
        Sentence can be corectly separated using default delimiter
        """
        wl = self.parserSpace.parseDefault("Howareyou")
        self.assertEqual(wl, ["Howareyou"])
        wl = self.parserSpace.parseDefault("How are you")
        self.assertEqual(wl, ["How", "are", "you"])
        wl = self.parserSpace.parseDefault("How are    you")
        self.assertEqual(wl, ["How", "are", "you"])
        wl = self.parserSpace.parseDefault("How are         you")
        self.assertEqual(wl, ["How", "are", "you"])
        # Ok that the two words are in separate lines, and separated by tab
        wl = self.parserSpace.parseDefault("How are  \n   \t    you")
        self.assertEqual(wl, ["How", "are", "you"])


    def test_parser_dot(self):
        """
        Sentence can be corectly separated by dot
        """
        wl = self.parserDot.parse("How.do.you.do")
        self.assertEqual(wl, ["How", "do", "you", "do"])


    def test_parser_strange_characters(self):
        """
        Test sentences containing strange characters
        """
        wl = self.parserSpace.parse("#%!@#!%! @#$!@#$")
        self.assertEqual(wl, ["#%!@#!%!", "@#$!@#$"])
        wl = self.parserSpace.parseDefault("#%!@#!%! \n\n\t\n\t\n\n\n@#$!@#$")
        self.assertEqual(wl, ["#%!@#!%!", "@#$!@#$"])
