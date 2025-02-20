import os
import ollama
import utils.config as config
import logging
from logging.handlers import QueueHandler
import sys
import multiprocessing


def get_all_image_paths(folder_path: str, logger) -> list[str]:
    logger.info(f"Scanning for images in: {folder_path}")
    image_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in config.IMAGES_TO_INCLUDE):
                image_paths.append(os.path.join(root, file))
    logger.info(f"Number of images found: {len(image_paths)}")
    return image_paths


def extract_info_image_with_llm(image_path: str):
    response = ollama.chat(
        model=config.MODEL_NAME,
        messages=[
            {
                'role': 'user',
                'content': config.PROMPT,
                'images': [image_path]
            }
        ]
    )   
    return response['message']['content']


def setup_logger(name, log_file, level=logging.INFO):
    """
    Setup a logger with a console handler and a file handler.
    The console handler will print to the console.
    The file handler will write to a file.

    Args:
        name (str): The name of the logger.
        log_file (str): The path to the log file.
        level (int): The logging level.

    Returns:
        logging.Logger: The logger.
    """
    
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler(log_file)

    # Set level for handlers
    c_handler.setLevel(level)
    f_handler.setLevel(level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger


def setup_worker_logger(queue: multiprocessing.Queue):
    """
    Setup a logger for a worker.
    The logger will write to a queue.
    """
    logger = logging.getLogger('worker')
    logger.handlers = []
    queue_handler = QueueHandler(queue)
    logger.addHandler(queue_handler)
    logger.setLevel(config.LOGGING_LEVEL)
    return logger


def log_listener(queue: multiprocessing.Queue, log_file_path: str, level: int):
    """
    Listener function that handles log records from the queue
    Uses the same log file as the main process.
    """
    # Setup logging to write to the same file as main process
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(processName)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

    while True:
        try:
            record = queue.get()
            if record is None:
                break
            # Get the root logger which writes to the main log file
            logger = logging.getLogger()
            logger.handle(record)
        except Exception:
            import sys, traceback
            print('Error in listener:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

