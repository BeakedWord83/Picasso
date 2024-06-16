import tkinter as tk
from unittest.mock import Mock, patch
import pytest

from menu import Menu


@pytest.fixture(scope='session')
def root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def parent(root):
    parent = Mock()
    parent.get_root = Mock(return_value=root)
    return parent


def test_menu_init(parent):
    menu = Menu(parent)
    assert isinstance(menu.frame, tk.Frame)
    assert menu.app == parent


def test_menu_new_board(parent):
    menu = Menu(parent)
    with patch('menu.messagebox.askquestion', return_value='yes'), \
            patch.object(parent, 'create_board') as mock_create_board:
        menu.new_board()
        mock_create_board.assert_called_once()


def test_menu_open_board(parent):
    menu = Menu(parent)
    filename = 'test.pcso'
    with patch('menu.filedialog.askopenfilename', return_value=filename), \
            patch.object(parent, 'load_board') as mock_load_board:
        menu.open_board()
        mock_load_board.assert_called_once_with(filename)


def test_menu_show(parent):
    menu = Menu(parent)
    with patch.object(menu.frame, 'pack') as mock_pack:
        menu.show()
        mock_pack.assert_called_once()


def test_menu_hide(parent):
    menu = Menu(parent)
    with patch.object(menu.frame, 'pack_forget') as mock_pack_forget:
        menu.hide()
        mock_pack_forget.assert_called_once()
