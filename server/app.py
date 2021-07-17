import logging

from flask import Flask, request

from server.services.service_manager import ServiceManager, ServiceType
from server.services.task_service import TaskType

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() " \
         "] %(message)s "
logging.basicConfig(format=FORMAT)

app = Flask(__name__)

service_manager = ServiceManager()
service_manager.init_services()


@app.route("/task/create/<string:task_type_str>", methods=['POST'])
def create_task(task_type_str):
    task_service = service_manager.get_service(ServiceType.TASK)
    if not task_service:
        return {"status": False}
    task_type = TaskType.from_str(task_type_str)
    if not task_type:
        return {"status": False}
    return {"status":task_service.create_task(task_type)}


@app.route("/task/get", methods=['GET'])
def get_task():
    task_service = service_manager.get_service(ServiceType.TASK)
    if not task_service:
        return {"status": False, "task": None}
    return {"status":True, "details": task_service.get_task()}


@app.route("/config/get", methods=['GET'])
def get_config():
    config_service = service_manager.get_service(ServiceType.CONFIG)
    if not config_service:
        return {"status": False}
    return {"status": True, "config": config_service.get()}


@app.route("/config/update", methods=['POST'])
def update_config():
    config = request.get_json()
    config_service = service_manager.get_service(ServiceType.CONFIG)
    if not config_service:
        return {"status": False}
    return {"status": True, "config": config_service.update(config)}


@app.route("/license/get", methods=['GET'])
def get_license():
    licence_service = service_manager.get_service(ServiceType.LICENSE)
    if not licence_service:
        return {"status": True, "details": {"key": "", "valid": False}}
    return {"status": True, "details": licence_service.get()}


if __name__ == "__main__":
    app.run()
