import json
import os

from appdirs import user_config_dir

from server.services.config_service import ConfigService
from server.services.license_service import LicenseService
from server.services.metadata_service import MetadataService
from server.services.service_type import ServiceType
from server.services.task_service import TaskService
from siosa.config.siosa_config import SiosaConfig

CONFIG_FILE_NAME = "config.json"


def _get_config_path():
    def parent(f): return os.path.dirname(os.path.abspath(f))

    config = os.path.join(parent(parent(__file__)), "config")
    config_file = os.path.join(config, CONFIG_FILE_NAME)
    return config_file


def _get_or_create_siosa_config():
    config_dir = user_config_dir('Siosa', '')
    config_file_path = os.path.join(config_dir, CONFIG_FILE_NAME)
    if os.path.exists(config_file_path):
        return SiosaConfig.create_from_file(config_file_path)

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    json.dump({}, open(config_file_path, 'w'), indent=4)
    return SiosaConfig.create_from_file(config_file_path)


class ServiceManager:
    def __init__(self):
        self.config = _get_or_create_siosa_config()
        self.services = {}

    def init_services(self):
        try:
            self.services[ServiceType.TASK] = \
                self._create_service(ServiceType.TASK)
        except:
            self.services[ServiceType.TASK] = None
        self.services[ServiceType.CONFIG] = \
            self._create_service(ServiceType.CONFIG)
        self.services[ServiceType.LICENSE] = \
            self._create_service(ServiceType.LICENSE)
        self.services[ServiceType.METADATA] = \
            self._create_service(ServiceType.METADATA)

    def get_service(self, service_type):
        if service_type in self.services:
            return self.services[service_type]
        return None

    def restart_service(self, service_type):
        service = self.services[service_type]
        if service:
            del service
        self.services[service_type] = self._create_service(service_type)

    def _create_service(self, service_type):
        if service_type == ServiceType.TASK:
            return TaskService(self.config)
        elif service_type == ServiceType.CONFIG:
            return ConfigService(self.config, _get_config_path())
        elif service_type == ServiceType.LICENSE:
            return LicenseService(self.config)
        elif service_type == ServiceType.METADATA:
            return MetadataService(self.config)
        return None
