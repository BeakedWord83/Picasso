import argparse
import tkinter
from app import App


def main() -> None:
    """
    The main function that starts the application.
    """
    parser = argparse.ArgumentParser(description="!!!IMPORTANT!!!:\n"
                                                 "RUN 'LANG=en_US' BEFORE RUNNING THE APPLICATION!\n"
                                                 "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n"
                                                 "Run 'python main.py' to start the GUI application.", formatter_class=argparse.RawTextHelpFormatter)
    parser.parse_known_args()

    # Create a new tkinter window
    root = tkinter.Tk()

    # Create a new App instance
    App(root)

    # Start the tkinter event loop
    root.mainloop()


if __name__ == '__main__':
    main()
