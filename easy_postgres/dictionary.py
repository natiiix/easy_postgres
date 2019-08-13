"""Module containing the smart `Dictionary` class."""


class Dictionary(dict):
    """
    Extended dictionary that supports access to items via attributes.
    """

    def __init__(self, source=None, **kwargs):
        """
        Initializes a new smart dictionary from a source object.
        If the source object is a dictionary, its items will be simply copied.
        Otherwise a new dictionary will be constructed from
        the source object's public non-callable attributes.
        Specified keyword arguments are added to the
        dictionary extracted from the source object.
        """

        if not source:
            dictionary = {}
        elif isinstance(source, dict):
            dictionary = source
        else:
            dictionary = {}

            for attr in dir(source):
                # Ignore private attributes
                if not attr.startswith("_"):
                    value = getattr(source, attr)
                    # Ignore functions
                    if not callable(value):
                        dictionary[attr] = value

        super().__init__({**dictionary, **kwargs})

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]
