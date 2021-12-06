import os
import sys


sys.path.insert(0, os.path.abspath("../.."))
print(os.path.abspath("../.."))
# -- Project information -----------------------------------------------------

project = "QA App Station"
copyright = "2021, Elakkiya"
author = "Elakkiya"

# The full version, including alpha/beta/rc tags
release = "0.0.1"


# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.extlinks",
]
extlinks = {
    "mdapp": (
        "https://kivymd.readthedocs.io/en/latest/themes/material-app/index.html#kivymd.app.MDApp",
        "mdapp",
    ),
    "kivyapp": (
        "https://kivy.org/doc/stable/api-kivy.app.html#kivy.app.App",
        "kivyapp",
    ),
    "func_partial": (
        "https://docs.python.org/3/library/functools.html#functools.partial",
        "func_partial",
    ),
    "kivy_builder": (
        "https://kivy.org/doc/stable/api-kivy.lang.builder.html",
        "kivy_builder",
    ),
    "screen_manager": (
        "https://kivy.org/doc/stable/api-kivy.uix.screenmanager.html",
        "screen_manager",
    ),
    "orb": (
        "https://iopscience.iop.org/article/10.1088/1742-6596/1237/3/032020/pdf",
        "orb",
    ),
    "orb_class": (
        "https://docs.opencv.org/3.4/db/d95/classcv_1_1ORB.html",
        "orb_class",
    ),
    "orb_detect": (
        "http://amroamroamro.github.io/mexopencv/matlab/cv.ORB.detectAndCompute.html",
        "orb_detect",
    ),
    "bf_matcher": (
        "https://docs.opencv.org/3.4/d3/da1/classcv_1_1BFMatcher.html",
        "bf_matcher",
    ),
    "find_contours": (
        "https://docs.opencv.org/3.4/d3/dc0/group__imgproc__shape.html#ga17ed9f5d79ae97bd4c7cf18403e1689a",
        "find_contours",
    ),
    "depthai_pipeline": (
        "https://docs.luxonis.com/projects/api/en/latest/references/python/#depthai.Pipeline",
        "depthai_pipeline",
    ),
    "oak_config": (
        "https://miro.com/welcomeonboard/TlJhTkZINVJkbVBVMkd0Z2NGWWowcDVjRmxYaDdHVTRYNGFnaUxESGozZTlRT0k5Y3UzbDJpNU1abVBZa3RWZ3wzMDc0NDU3MzUyMTgzMjQ1MjA0",
        "oak_config",
    ),
    "pyzbar": (
        "https://pypi.org/project/pyzbar/",
        "pyzbar",
    ),
    "clock": ("https://kivy.org/doc/stable/api-kivy.clock.html", "clock"),
    "main_window": (
        "https://drive.google.com/file/d/1cbIK_xqZofoy2yS_ITaUgbJq87HHzFJB/view?usp=sharing",
        "main_window",
    ),
    "dashboard": (
        "https://drive.google.com/file/d/1Sm18gzY0QM8JsbcNeEw9hmSzKZe8tbwM/view?usp=sharing",
        "dashboard",
    ),
    "search_screen": (
        "https://drive.google.com/file/d/1k3pDAa1hvT7hjmp88pAzcF0m3rR5ofWA/view?usp=sharing",
        "search_screen",
    ),
    "kivy_text": (
        "https://kivy.org/doc/stable/api-kivy.uix.textinput.html#",
        "kivy_text",
    ),
    "hydra_data": (
        "https://docs.python.org/3.7/library/dataclasses.html",
        "hydra_data",
    ),
    "omegaconf": (
        "https://omegaconf.readthedocs.io/en/latest/structured_config.html",
        "omegaconf",
    ),
    "app_demo": (
        "https://drive.google.com/file/d/1A3jBE7nzir5S63-y1cDki4LhMiRuUxPx/view?usp=sharing",
        "app_demo",
    ),
}
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
}
napoleon_google_docstring = False
napoleon_use_param = True
napoleon_use_ivar = True
templates_path = ["_templates"]
todo_include_todos = True
autodoc_mock_imports = [
    "kivy",
    "kivymd",
    "hydra",
    "depthai",
    "cv2",
    "pyzbar",
    "omegaconf",
    "numpy",
    "yaml",
    "hydra.utils",
]
# Usually you set "language" from the command line for these cases.
language = "python"

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_path = ["."]
html_static_path = ["_static"]
