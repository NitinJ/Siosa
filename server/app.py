import logging

from flask import Flask, request

from server.services.service_manager import ServiceManager, ServiceType

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() " \
         "] %(message)s "
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    handlers={
        logging.FileHandler('siosa-server.log', encoding='utf-8'),
        logging.StreamHandler()
    }
)

app = Flask(__name__)

service_manager = ServiceManager()
service_manager.init_services()


# ##############################################################################
# Tasks
@app.route("/task/create/test", methods=['POST'])
def create_test_task():
    task_service = service_manager.get_service(ServiceType.TASK)
    if not task_service:
        return {"status": False}

    return {"status": task_service.create_test_task()}


@app.route("/task/create/trade", methods=['POST'])
def create_trade_task():
    task_service = service_manager.get_service(ServiceType.TASK)
    if not task_service:
        return {"status": False}

    return {"status": task_service.create_trade_task()}


@app.route("/task/create/roll", methods=['POST'])
def create_roll_task():
    config = request.get_json()
    if not config:
        return {"status": False}

    task_service = service_manager.get_service(ServiceType.TASK)
    if not task_service:
        return {"status": False}

    return {"status": task_service.create_roll_task(config)}


@app.route("/task/get", methods=['GET'])
def get_task():
    task_service = service_manager.get_service(ServiceType.TASK)
    if not task_service:
        return {"status": False}

    return {"status": True, "details": task_service.get_task()}


# ##############################################################################
# Config
@app.route("/config/get", methods=['GET'])
def get_config():
    config_service = service_manager.get_service(ServiceType.CONFIG)
    if not config_service:
        return {"status": False}

    return {"status": True, "details": {"config": config_service.get()}}


@app.route("/config/update", methods=['POST'])
def update_config():
    config = request.get_json()
    if not config:
        return {"status": False}

    config_service = service_manager.get_service(ServiceType.CONFIG)
    if not config_service:
        return {"status": False}

    return {"status": True,
            "details": {"config": config_service.update(config)}}


# ##############################################################################
# License
@app.route("/license/register", methods=['POST'])
def register_license():
    data = request.get_json()
    if not data:
        return {"status": False}

    licence_service = service_manager.get_service(ServiceType.LICENSE)
    if not licence_service:
        return {"status": False}

    return {
        "status": True,
        "details": licence_service.register(data['key'])
    }


@app.route("/license/get", methods=['GET'])
def get_license():
    licence_service = service_manager.get_service(ServiceType.LICENSE)
    if not licence_service:
        return {"status": False}

    return {"status": True, "details": licence_service.get()}


if __name__ == "__main__":
    app.run()
