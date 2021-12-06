import kivy
import yaml
import io
from ..utils import utils as rp  # ..


string = rp.relative_to_abs_path("..src/ui/screens/conf/dashboard.yaml")  # ..
with io.open(string, "r") as stream:
    """
    Reads ``kv`` configurations form a ``.yaml`` file and loads
    it to a  variable``
    """
    dashboard_conf = yaml.safe_load(stream)

fields = {
    "width": "Width",
    "length": "Length",
    "depth": "Height",
    "act_wgt": "Actual weight",
    "exp_wgt": "Expected weight",
}

colors = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#006400",
    "cyan": "#728F9B",
    "gray": "#808080",
    "lime": "#32CD32",
    "tomato": "#FF6347",
    "orange": "#FFA500",
    "teal": "#008080",
}

palette = (
    [0.28627450980392155, 0.8431372549019608, 0.596078431372549, 1],
    [0.3568627450980392, 0.3215686274509804, 0.8666666666666667, 1],
    [0.8862745098039215, 0.36470588235294116, 0.592156862745098, 1],
    [0.8784313725490196, 0.9058823529411765, 0.40784313725490196, 1],
)
wms_response = {
    "334456": {
        "transfer_id": 334456,
        "name": "Oak-D camera ",
        "sku": "https://qrco.de/bc5V4T",
        "state": "awaiting qa",
        "barcode_id": "https://qrco.de/bc5V4T",
        "metrics": ["cm", "g"],
        "dimensions": {"width": 11, "length": 20, "depth": 7.7},
        "weight": 500,
        "quantity": 40,
    },
    "23456": {
        "transfer_id": 23456,
        "name": "Oak-D",
        "sku": "https://qrco.de/bc5V4T",
        "state": "completed",
        "barcode_id": "https://qrco.de/bc5V4T",
        "metrics": ["cm", "g"],
        "dimensions": {"width": 2.3, "length": 5.5, "depth": 4.7},
        "weight": 750,
        "quantity": 18,
    },
    "98765": {
        "transfer_id": 98765,
        "name": "AI Kit",
        "sku": "https://qrco.de/bc5V4T",
        "state": "flagged",
        "barcode_id": "https://qrco.de/bc5V4T",
        "metrics": ["cm", "g"],
        "dimensions": {"width": 7, "length": 1.5, "depth": 1.7},
        "weight": 75,
        "quantity": 23,
    },
    "https://qrco.de/bc5V4T": {
        "transfer_id": 12345,
        "name": "Oak-D camera ",
        "sku": "https://qrco.de/bc5V4T",
        "state": "awaiting qa",
        "barcode_id": "https://qrco.de/bc5V4T",
        "metrics": ["cm", "g"],
        "dimensions": {"width": 11, "length": 20, "depth": 7.7},
        "weight": 500,
        "quantity": 40,
    },
}
