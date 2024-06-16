import tkinter as tk
import pytest
from unittest.mock import Mock, patch
from width_dialog import WidthDialog


@pytest.fixture(scope='session')
def tk_root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def width_dialog(tk_root):
    return WidthDialog(tk_root, 5)


def test_width_dialog_initializes_correctly(width_dialog):
    assert width_dialog.title() == "Change Width"
    assert width_dialog.result == 0
    assert width_dialog.slider.get() == 5


def test_width_dialog_ok(width_dialog):
    width_dialog.slider.set(8)
    width_dialog.destroy = Mock()

    width_dialog.ok()

    assert width_dialog.result == 8
    width_dialog.destroy.assert_called_once()