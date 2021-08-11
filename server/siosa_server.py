import logging

from flask import Flask, request

from server.services.service_manager import ServiceManager, ServiceType
from siosa.config.metadata import get_metadata

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


@app.route("/task/create/roller", methods=['POST'])
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


@app.route("/task/stop", methods=['POST'])
def stop_task():
    task_service = service_manager.get_service(ServiceType.TASK)
    if not task_service:
        return {"status": False}

    return {"status": True, "details": task_service.stop_all_tasks()}

# ##############################################################################
# Config
@app.route("/config/get", methods=['GET'])
def get_config():
    config_service = service_manager.get_service(ServiceType.CONFIG)
    metadata_service = service_manager.get_service(ServiceType.METADATA)
    if not config_service or not metadata_service:
        return {"status": False}

    config_data = config_service.get()
    stashes = metadata_service.get_stashes()
    leagues = metadata_service.get_leagues()
    config_metadata = get_metadata()
    for field in config_metadata:
        if field['name'] in ('sell', 'dump', 'currency'):
            field['values'] = [stash['n'] for stash in stashes]
        if field['name'] == 'league':
            field['values'] = [league['id'] for league in leagues]

    config_data.update({"metadata": config_metadata})
    return {"status": True, "details": config_data}


@app.route("/config/update", methods=['POST'])
def update_config():
    config = request.get_json()
    if not config:
        return {"status": False}

    config_service = service_manager.get_service(ServiceType.CONFIG)
    if not config_service:
        return {"status": False}

    return {"status": True,
            "details": config_service.update(config)}


# ##############################################################################
# Metadata
@app.route("/metadata/get_stashes", methods=['GET'])
def get_stashes():
    metadata_service = service_manager.get_service(ServiceType.METADATA)
    if not metadata_service:
        return {"status": False}

    return {"status": True, "stashes": metadata_service.get_stashes()}

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
