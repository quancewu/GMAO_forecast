import logging
import threading
import os,time
import yaml

def logging_config_init(ex_path):
    ex_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(ex_path,'config','logging.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    config['handlers']['info_file_handler']['filename'] = os.path.join(ex_path,'log_file','debug.log')
    config['handlers']['error_file_handler']['filename'] = os.path.join(ex_path,'log_file','errors.log')
    with open(path, 'w') as file:
        documents = yaml.dump(config, file)

def logging_start(ex_path):
    # ex_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(ex_path,'config','logging.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)