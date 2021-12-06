import hydra

# from ..utils import resource_paths as rp
from hydra.core.config_store import ConfigStore
from hydra.experimental import compose, initialize
from omegaconf import MISSING, OmegaConf
from ..utils import utils  # ..
from dataclasses import dataclass
from typing import List


@dataclass
class ModelConfig:
    """Loads the deep learning model configurations based on the
    ``driver`` name in runtime"""

    driver: str = MISSING
    label_map: List = MISSING


@dataclass
class MobileNetConfig(ModelConfig):
    """Loads the ``mobilenetssd`` model configuration"""

    driver: str = "mobilenetssd"
    blob_fpath: str = MISSING
    blob_config_fpath: str = MISSING
    input_size_x: int = MISSING
    input_size_y: int = MISSING


@dataclass
class EfficientNetConfig(ModelConfig):
    """Loads the ``efficientnet`` model configuration"""

    driver: str = "efficientnet"
    blob_fpath: str = MISSING
    blob_config_fpath: str = MISSING


@dataclass
class CvConfig:
    """Loads the computer vision configurations for object measurement
    based on the ``driver`` name in runtime"""

    driver: str = MISSING
    resize_window_min: int = MISSING
    resize_window_max: int = MISSING
    area_min: int = MISSING
    area_max: int = MISSING
    thres_min: int = MISSING
    thres_max: int = MISSING
    thres_limit: int = MISSING


@dataclass
class CvDefaultConfig(CvConfig):
    """Loads the ``cv_default`` CV configuration"""

    driver: str = "cv_default"
    scale_factor_x: float = MISSING
    scale_factor_y: float = MISSING
    kernel_gauss: int = MISSING
    iter_gauss: int = MISSING
    kernel_dilate: int = MISSING
    iter_dilate: int = MISSING
    r_color: int = MISSING
    g_color: int = MISSING
    b_color: int = MISSING
    display: bool = MISSING
    debug: bool = MISSING


@dataclass
class CvCustomConfig(CvConfig):
    """Loads the ``cv_custom_001`` CV configuration"""

    driver: str = "cv_custom_001"


@dataclass
class CalibConfig:
    """Please refer to :hydra_data:`Hydra dataclass <>` for more details

    .. note::
       Assign MISSING to a field to indicates that it does not have a default value.
       This is equivalent to the ??? literal we have seen in OmegaConf configurations before.

       Omitting a default value is equivalent to assigning MISSING to it, although it is
       sometimes convenient to be able to assign MISSING it to a field.
    """

    driver: str = MISSING
    left_mesh_fpath: str = MISSING
    right_mesh_fpath: str = MISSING
    right_map_x_fpath: str = MISSING
    right_map_y_fpath: str = MISSING
    left_map_x_fpath: str = MISSING
    left_map_y_fpath: str = MISSING


@dataclass
class OakDConfig(CalibConfig):
    """Loads the ``oakd`` camera configuration"""

    driver: str = "oakd"
    custom_calib_fpath: str = MISSING
    interleaved_color_cam: bool = MISSING
    output_depth_stereo: bool = MISSING
    thres_conf_stereo: int = MISSING
    thres_conf_spatial: float = MISSING
    blocking_spatial: bool = MISSING
    bb_scale_factor_spatial: float = MISSING
    depth_low_thres_spatial: int = MISSING
    depth_high_thres_spatial: int = MISSING
    out_queue_blocking: bool = MISSING
    out_queue_max_size: int = MISSING
    base_depth: int = MISSING
    syncnn: bool = MISSING
    full_frame_tracking: bool = MISSING


@dataclass
class CustomCamConfig(CalibConfig):
    """Loads ``customcam`` camera configuration"""

    driver: str = "customcam"
    custom_calib_fpath: str = MISSING


@dataclass
class DbConfig:
    """Loads the DB configurations for
    based on the ``driver`` name in runtime

    .. note::
        Please note that at the momemt there is no DB
        connections available"""

    driver: str = MISSING


@dataclass
class QaDbConfig(DbConfig):
    """Loads ``qa_db`` DB configuration"""

    driver: str = "qa_db"
    img_class_fpath: str = MISSING
    fwrite_fpath: str = MISSING


@dataclass
class ProdDbConfig(DbConfig):
    """Loads ``prod_db`` DB configuration"""

    driver: str = "prod_db"
    custom_calib_fpath: str = MISSING


@dataclass
class StagingDbConfig(DbConfig):
    """Loads ``stag_db`` DB configuration"""

    driver: str = "stag_db"
    custom_calib_fpath: str = MISSING


@dataclass
class Config:
    model: ModelConfig = MISSING
    calib: CalibConfig = MISSING
    db: DbConfig = MISSING
    cv: CvConfig = MISSING


cs = ConfigStore.instance()
cs.store(
    group="schema/model",
    name="mobilenetssd",
    node=MobileNetConfig,
    package="model",
)
cs.store(
    group="schema/model",
    name="efficientnet",
    node=EfficientNetConfig,
    package="model",
)
cs.store(group="schema/calib", name="oakd", node=OakDConfig, package="calib")
cs.store(
    group="schema/calib",
    name="customcam",
    node=CustomCamConfig,
    package="calib",
)
cs.store(
    group="schema/db",
    name="qa_db",
    node=QaDbConfig,
    package="db",
)
cs.store(group="schema/db", name="prod_db", node=ProdDbConfig, package="db")
cs.store(
    group="schema/db",
    name="stag_db",
    node=StagingDbConfig,
    package="db",
)
cs.store(group="schema/cv", name="cv_default",
         node=CvDefaultConfig, package="cv")
cs.store(
    group="schema/cv",
    name="cv_custom_001",
    node=CvCustomConfig,
    package="cv",
)
cs.store(name="config", node=Config)


@hydra.main(config_path="conf", config_name="configs")
def load_config(cfg: Config) -> None:
    """Loads the OmegaConf's Structured configurations via the ``ConfigStore``
    API configuration file.

    .. note::
        More information about :omegaconf:`OmegaConf's structured configuration <>`

    Parameters
    ----------
    cfg :
        Manages structured configuration
    """
    print(OmegaConf.to_yaml(cfg))


hydra.initialize(config_path="conf", job_name="test_app")
cfg = hydra.compose(config_name="configs")
