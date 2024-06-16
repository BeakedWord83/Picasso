import pytest
import tkinter as tk
from unittest.mock import patch, Mock

from menu_handler import MenuHandler


@pytest.fixture(scope='session')
def root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def menu_handler(root):
    board = Mock()
    board.app.get_root = Mock(return_value=root)
    board.app.get_root().config = Mock()
    board.canvas = tk.Canvas(root)
    board.object_editor = Mock()
    menu_handler = MenuHandler(board)
    return menu_handler


def test_setup_menu(menu_handler):
    assert isinstance(menu_handler.menu, tk.Menu)
    menu_handler.board.app.get_root.return_value.config.assert_called_once_with(menu=menu_handler.menu)


@patch('tkinter.Menu.post')
def test_display_context_menu(mock_post, menu_handler):
    event = Mock()
    item_type = "line"
    with patch.object(menu_handler, 'display_line_context_menu') as mock_display_line_context_menu:
        menu_handler.display_context_menu(event, item_type)
        mock_display_line_context_menu.assert_called_once_with(event)

    item_type = "text"
    with patch.object(menu_handler, 'display_text_context_menu') as mock_display_text_context_menu:
        menu_handler.display_context_menu(event, item_type)
        mock_display_text_context_menu.assert_called_once_with(event)

    item_type = "rectangle"
    with patch.object(menu_handler, 'display_shape_context_menu') as mock_display_shape_context_menu:
        menu_handler.display_context_menu(event, item_type)
        mock_display_shape_context_menu.assert_called_once_with(event)


@patch('tkinter.Menu.post')
def test_paste_context_menu(mock_post, menu_handler):
    event = Mock()
    menu_handler.paste_context_menu(event)
    mock_post.assert_called_once_with(event.x_root, event.y_root)


@patch('tkinter.Menu.post')
def test_display_line_context_menu(mock_post, menu_handler):
    event = Mock()
    menu_handler.display_line_context_menu(event)
    mock_post.assert_called_once_with(event.x_root, event.y_root)


@patch('tkinter.Menu.post')
def test_display_text_context_menu(mock_post, menu_handler):
    event = Mock()
    menu_handler.display_text_context_menu(event)
    mock_post.assert_called_once_with(event.x_root, event.y_root)


@patch('tkinter.Menu.post')
def test_display_shape_context_menu(mock_post, menu_handler):
    event = Mock()
    menu_handler.display_shape_context_menu(event)
    mock_post.assert_called_once_with(event.x_root, event.y_root)
