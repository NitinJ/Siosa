from siosa.config import utils
from siosa.config.siosa_config import SiosaConfig
from siosa.network.poe_api import PoeApi


class MetadataService:
    def __init__(self, siosa_config: SiosaConfig):
        self.config = siosa_config

    def get_stashes(self):
        if self.config.is_valid():
            return utils.get_stash_metadata(self.config.to_json())
        return []

    def get_leagues(self):
        return PoeApi.get_leagues()
