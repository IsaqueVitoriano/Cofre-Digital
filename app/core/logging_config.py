import logging.config
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGGING_FILE= BASE_DIR / "config" / "logging.yaml"

with open(LOGGING_FILE, 'r', encoding="utf-8") as file:
    config= yaml.safe_load(file)

config= config["logging"]

config["handlers"]["app_file"]["filename"]= str(BASE_DIR / "storage" / "logs" / "app.log")
config["handlers"]["atividades_file"]["filename"]= str(BASE_DIR / "storage" / "logs" / "atividade.log")

logging.config.dictConfig(config)

logger = logging.getLogger("cofre_api")
atividades_logger = logging.getLogger("cofre_atividades")

logger.info("Sistema de loggin inicializado com sucesso!")