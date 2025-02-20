import logging

DATA_PATH = 'data/imgs'
IMAGES_TO_INCLUDE = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.webp']

# Pallalization Params
RUN_PARALLEL = True
NUM_WORKERS = 20
TIMEOUT = 60

# Logging Params
LOG_PATH = 'data/logs'
LOG_FILE_NAME = 'pipeline_run.log'
LOGGING_LEVEL = logging.DEBUG # e.g, logging.DEBUG, logging.INFO

# Model Params
MODEL_NAME = 'llava'
PROMPT = """
    Describe this image. Extract all text information inf present.
    """