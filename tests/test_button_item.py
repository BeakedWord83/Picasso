import pytest
import tkinter as tk
from PIL import Image
from PIL.ImageTk import PhotoImage
from button_item import ButtonItem


@pytest.fixture(scope="session")
def button():
    root = tk.Toplevel()
    button = tk.Button(root)
    yield button
    root.destroy()


@pytest.fixture
def image():
    img = Image.new('RGB', (100, 100), color='red')
    photo_image = PhotoImage(img)
    yield photo_image


def test_button_item_initialization(button, image):
    button_item = ButtonItem(button, image)
    assert button_item.button == button
    assert button_item.image == image


def test_button_item_attributes(button, image):
    button_item = ButtonItem(button, image)
    assert isinstance(button_item.button, tk.Button)
    assert isinstance(button_item.image, PhotoImage)
