class FallbackFont:
    """
    A class representing a fallback font with a name and size.
    """

    DEFAULT_FONT_NAME = "Arial"

    def __init__(self, size: int) -> None:
        """
        Initialize the FallbackFont.

        :param size: The size of the font.
        """
        self.name: str = FallbackFont.DEFAULT_FONT_NAME
        self.size: int = size
