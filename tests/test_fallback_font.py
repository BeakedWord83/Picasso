import pytest
from fallback_font import FallbackFont


def test_fallback_font_initialization():
    size = 12
    fallback_font = FallbackFont(size)
    assert fallback_font.name == "Arial"
    assert fallback_font.size == size


def test_fallback_font_attributes():
    size = 14
    fallback_font = FallbackFont(size)
    assert isinstance(fallback_font.name, str)
    assert isinstance(fallback_font.size, int)


@pytest.mark.parametrize("size", [10, 12, 14, 16])
def test_fallback_font_size(size):
    fallback_font = FallbackFont(size)
    assert fallback_font.size == size
