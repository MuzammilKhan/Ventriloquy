
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
