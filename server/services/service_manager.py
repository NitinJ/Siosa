import os

from server.services.config_service import ConfigService
from server.services.license_service import LicenseService
from server.services.service_type import ServiceType
from server.services.task_service import TaskService
from siosa.config.siosa_config import SiosaConfig


def _get_config_path():
    def parent(f): return os.path.dirname(os.path.abspath(f))

    config = os.path.join(parent(parent(__file__)), "config")
    config_file = os.path.join(config, ServiceManager.CONFIG_FILE_NAME)
    return config_file


class ServiceManager:
    CONFIG_FILE_NAME = "config.json"

    def __init__(self):
        self.config = SiosaConfig.create_from_file(_get_config_path())
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
        return None
