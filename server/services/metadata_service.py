from siosa.config import utils
from siosa.config.siosa_config import SiosaConfig


class MetadataService:
    def __init__(self, siosa_config: SiosaConfig):
        self.config = siosa_config

    def get_stashes(self):
        return utils.get_stash_metadata(self.config.to_json())
