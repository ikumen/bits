import os
import dotenv
import logging

from uvicorn.logging import ColourizedFormatter

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
dotenv.load_dotenv(dotenv_path)


class Config:
    APP_NAME = os.environ['APP_NAME']
    LOG_LVL = logging.getLevelName(int(os.environ['LOG_LVL']))

    FIRESTORE_PROJECT_ID = os.environ['FIRESTORE_PROJECT_ID']


config = Config()

logging.basicConfig(level=config.LOG_LVL,
    format='%(asctime)s| %(levelname)-8s| %(name)s - %(message)s')
