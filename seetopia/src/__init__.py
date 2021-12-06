import sys
import os
from .qa_app_demo import QAApp
from kivy.resources import resource_add_path


def main():
    """
    .. note::
        Please watch the demo of :app_demo:`QAApp <>`

    .. warning::
        If pyinstaller path attribution is created, then add it to the
        resource path which will update the absolute path to the bundle
        folder.

    >>> resource_add_path(os.path.join(sys._MEIPASS))

    """
    if hasattr(sys, "_MEIPASS"):
        resource_add_path(os.path.join(sys._MEIPASS))
    QAApp().run()


if __name__ == "__main__":
    main()