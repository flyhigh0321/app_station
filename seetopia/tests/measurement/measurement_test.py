from measurement import __version__
from measurement.object_measurement import CONSTANVT


def test_version():
    assert __version__ == "0.1.0"
    assert CONSTANVT == "name"


def measurement_subject():
    pass


a = {"user": "name", "add": "value"}
