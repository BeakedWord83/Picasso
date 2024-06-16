import tkinter as tk
import pytest
from unittest.mock import Mock
from font_dialog import FontDialog


@pytest.fixture(scope='session')
def tk_root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def font_dialog(tk_root):
    return FontDialog(tk_root, "Arial")


def test_font_dialog_initializes_correctly(font_dialog):
    assert font_dialog.title() == "Change Font"
    assert font_dialog.result is None
    assert font_dialog.font_var.get() == "Arial"


def test_font_dialog_on_ok(font_dialog):
    font_dialog.font_var.set("Courier")
    font_dialog.destroy = Mock()

    font_dialog.on_ok()

    assert font_dialog.result == "Courier"
    font_dialog.destroy.assert_called_once()


def test_font_dialog_on_cancel(font_dialog):
    font_dialog.destroy = Mock()

    font_dialog.on_cancel()

    font_dialog.destroy.assert_called_once()
