import utils.config as config
from utils.helper import get_all_image_paths, extract_info_image_with_llm, log_listener, setup_worker_logger
import multiprocessing
from multiprocessing import Manager
import concurrent.futures
import logging


def extract_info_per_image(image_path: str, logger):

    logger.info(f"Extracting info for {image_path}")

    output = {
        "image_path": image_path, 
        "status": "Failed", 
        "error": "None", 
        "info": "None"
        }
    
    info = extract_info_image_with_llm(image_path)

    output["status"] = "Success"
    output["info"] = info

    return output


def run_with_timeout(func, image_path, *args, **kwargs):
    """
    Function to run each image parallelly with timeout
    """

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, image_path, *args, **kwargs)
        try:
            output = future.result(timeout=config.TIMEOUT)
            return output
        
        except concurrent.futures.TimeoutError:
            output = {
                "image_path": image_path, 
                "status": "Failed", 
                "error": f"TimeoutError: Exceeded {config.TIMEOUT} Secs", 
                "info": "None"
                }
            return output
        
        except Exception as e:
            output = {
                "image_path": image_path, 
                "status": "Failed", 
                "error": str(e),
                "info": "None"
                }
            return output


def extract_info(image_path, shared_dict):
    """
    Wrapper for extract_info_per_image that uses worker logger
    """
    logger = setup_worker_logger(shared_dict['log_queue'])
    return extract_info_per_image(image_path, logger)


def parallel_extract_info_all_images(image_paths: list[str], logger):

    logger.info("Parallel processing starts...")
    if config.RUN_PARALLEL and (config.NUM_WORKERS > 1):
        # Ensure num_workers does not go beyond limit
        num_workers = min((multiprocessing.cpu_count()-2), config.NUM_WORKERS)
    else:
        num_workers = 1 # Force to serial processing

    logger.debug(f"Number of workers called: {num_workers}")

    # Get the main log file path from the logger's handlers
    main_log_file = None
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            main_log_file = handler.baseFilename
            break

    if main_log_file is None:
        raise ValueError("Cannot find main log file path")
    
    with Manager() as manager:
        shared_dict = manager.dict()
        shared_dict['log_queue'] = manager.Queue()

        # Start the listener process using the main log file
        listener = multiprocessing.Process(
            target=log_listener,
            args=(shared_dict['log_queue'],
                  main_log_file,
                  logger.level)
        )
        listener.start()

        results = []
        try:
            logger.info(f"Processing images...")

            with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
                future_to_images = {
                    executor.submit(
                        run_with_timeout,
                        extract_info,
                        image_path,
                        shared_dict=shared_dict
                    ): image_path for image_path in image_paths
                }

                for future in concurrent.futures.as_completed(future_to_images):
                    try:
                        result = future.result(timeout=config.TIMEOUT)
                        results.append(result)
                    except Exception:
                        raise
        
        finally:
            # Signal the listner to stop and clean up
            shared_dict['log_queue'].put(None)
            listener.join()

    logger.info("Parallel processing done.")

    return results



if __name__ == "__main__":
    import os
    from utils.helper import setup_logger

    # Setup logger
    os.makedirs(config.LOG_PATH, exist_ok=True)
    log_file_path = os.path.join(config.LOG_PATH, config.LOG_FILE_NAME)
    logger = setup_logger('run_pipeline', log_file_path, level=config.LOGGING_LEVEL)

    image_paths = get_all_image_paths(config.DATA_PATH, logger)
    results = parallel_extract_info_all_images(image_paths, logger)

    print(results)

