import logging

log_format = "%(asctime)s %(levelname)s: %(message)s"
date_format = "%d-%m-%Y %H:%M:%S"

formatter = logging.Formatter(log_format, datefmt=date_format)

def create_logger(name, log_file, level=logging.INFO, to_console=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # prevent duplicate logs if root logger is configured

    # File handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

request_logger = create_logger("request-logger", "requests.log", logging.INFO, True)
stack_logger = create_logger("stack-logger", "stack.log", logging.INFO)
independent_logger = create_logger("independent-logger", "independent.log", logging.DEBUG)


######################################################################################################
#functions to help implement##########################################################################
######################################################################################################

request_counter = 0
request_start_times = 0

def addDitsToRequestLog(typeOfLog, resourceName = None, httpVerb = None):
    global request_counter, request_start_times
    import time

    if(typeOfLog == logging.INFO):
        request_counter += 1
        #TODO: make sure the verb is capital case
        log_details = f"Incoming request | #{request_counter} | resource: {resourceName} | HTTP Verb {httpVerb.upper()}"
        request_logger.info(log_details)
        #TODO: start timer
        request_start_time = time.perf_counter()

    elif(typeOfLog == logging.DEBUG):
        # TODO: add timer
        duration = (time.perf_counter() - request_start_times) * 1000  # ms
        log_details = f"request #{request_counter} duration: {duration}ms"
        request_logger.debug(log_details)