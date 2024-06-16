import tkinter as tk
import pytest
from unittest.mock import Mock
from font_size_dialog import FontSizeDialog


@pytest.fixture(scope='session')
def tk_root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def font_size_dialog(tk_root):
    return FontSizeDialog(tk_root, "12")


def test_font_size_dialog_initializes_correctly(font_size_dialog):
    assert font_size_dialog.title() == "Change Font Size"
    assert font_size_dialog.result is None
    assert font_size_dialog.size_var.get() == "12"


def test_font_size_dialog_on_ok(font_size_dialog):
    font_size_dialog.size_var.set("16")
    font_size_dialog.destroy = Mock()

    font_size_dialog.on_ok()

    assert font_size_dialog.result == "16"
    font_size_dialog.destroy.assert_called_once()


def test_font_size_dialog_on_cancel(font_size_dialog):
    font_size_dialog.destroy = Mock()

    font_size_dialog.on_cancel()

    font_size_dialog.destroy.assert_called_once()
