
class InputParser:
    """
    Class for parsing a string of words separated by a delimiter

    """
    def __init__(self, delim):
        self.delim = delim

    def parse(self, s):
        """
        Parsing the string using the delimiter

        Parameters
        ------
            s -- a string of tokens to be parse (separated)


        Return
        ------
            wl -- a list of token separated using the delimiter
        """
        wl = s.split(self.delim)
        return wl

    def parseDefault(self, s):
        """
        Parsing the string using the default delimiter, the strength of default
        delimiter is that the TAB and carrige return will also be ignored.

        Parameters
        ------

        Return
        ------
            wl -- a list of token separated using the delimiter
        """
        wl = s.split()
        return wl
