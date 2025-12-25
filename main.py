# main.py
import ttkbootstrap as tb
from gui.controller import CollatzGui

"""
Application entry point.

This module is responsible only for:
- initializing the GUI framework
- creating the root window
- starting the main event loop
"""
if __name__ == "__main__":
    # Create the ttkbootstrap root window
    root = tb.Window(themename="flatly")

    # Instantiate the main GUI controller
    CollatzGui(root)

    # Start the ttkbootstrap event loop
    root.mainloop()

