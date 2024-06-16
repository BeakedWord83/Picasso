import os
from unittest.mock import MagicMock, patch

import tkinter as tk
import pytest

from app import App


@pytest.fixture(scope="session")
def root():
    root = tk.Toplevel()
    yield root
    root.destroy()


@pytest.fixture
def app(root):
    app = App(root)
    return app


def test_get_root(app):
    assert app.get_root() == app._App__root


def test_show_menu_window(app):
    with patch.object(app.menu, 'show') as mock_show:
        app.show_menu_window()
        mock_show.assert_called_once()


def test_create_board(app):
    with patch.object(app.menu, 'hide') as mock_hide, \
            patch('app.Toolbox') as mock_toolbox, \
            patch('app.Board') as mock_board:
        app.create_board()
        mock_hide.assert_called_once()
        mock_toolbox.assert_called_once_with(app)
        mock_board.assert_called_once_with(app, mock_toolbox.return_value, app.loaded_fonts)


def test_load_fonts(app):
    font_dir = "fonts"
    font_files = ["font1.ttf", "font2.ttf"]

    with patch('os.listdir', return_value=font_files), \
            patch('os.path.join', side_effect=lambda x, y: f"{x}/{y}"), \
            patch('pyglet.font.add_file') as mock_add_file, \
            patch('pyglet.font.load') as mock_load:
        app.load_fonts()

        assert mock_add_file.call_count == len(font_files)
        assert mock_load.call_count == len(font_files) * 17  # 17 font sizes from 8 to 72 in steps of 4

        for font_file in font_files:
            font_name = os.path.splitext(font_file)[0]
            font_path = os.path.join(font_dir, font_file)
            mock_add_file.assert_any_call(font_path)

            for size in range(8, 73, 4):
                mock_load.assert_any_call(font_name, size)
                assert (font_name, size) in app.loaded_fonts


def test_load_board(app):
    filename = "board.json"
    board_state = {
        "objects": [
            {"type": "rect", "x": 100, "y": 200, "width": 300, "height": 400},
            {"type": "circle", "x": 500, "y": 600, "radius": 150}
        ]
    }

    with patch('builtins.open', MagicMock()), \
            patch('json.load', return_value=board_state), \
            patch.object(app.menu, 'hide') as mock_hide, \
            patch('app.Toolbox') as mock_toolbox, \
            patch('app.Board') as mock_board:
        app.load_board(filename)

        mock_hide.assert_called_once()
        mock_toolbox.assert_called_once_with(app)
        mock_board.assert_called_once_with(app, mock_toolbox.return_value, app.loaded_fonts)
        mock_board.return_value.file_handler.load_objects.assert_called_once_with(board_state['objects'])
