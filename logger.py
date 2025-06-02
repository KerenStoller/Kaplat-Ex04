######################################################################################################
#                                   logger creation                                                  #
######################################################################################################


import logging
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

log_format = "%(asctime)s %(levelname)s: %(message)s | request #%(request_number)s "
date_format = "%d-%m-%Y %H:%M:%S"
formatter = logging.Formatter(log_format, datefmt=date_format)

def create_logger(name, log_file, level=logging.INFO, to_console=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # prevent duplicate logs if root logger is configured

    # Create full log file path inside logs/ directory
    log_path = os.path.join("logs", log_file)

    # File handler
    file_handler = logging.FileHandler(log_path, mode='w')
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
logs = [request_logger, stack_logger, independent_logger]



######################################################################################################
#                                   functions to write logs                                          #
######################################################################################################



import time
request_counter = 0
request_start_time = 0

def addInfoLogToRequest(resource_name, http_verb):
    global request_start_time
    request_start_time = time.perf_counter()
    global request_counter
    request_counter += 1
    log_details = f"Incoming request | #{request_counter} | resource: {resource_name} | HTTP Verb {http_verb.upper()}"
    request_logger.info(log_details, extra={"request_number": request_counter})


def addDebugLogToRequest():
    global request_counter
    global request_start_time
    duration = (time.perf_counter() - request_start_time) * 1000  # ms
    duration = round(duration, 1)
    log_details = f"request #{request_counter} duration: {duration:.1f}ms"
    request_logger.debug(log_details, extra={"request_number": request_counter})


def addErrorLog(logger, message):
    global request_counter
    logger.error(f"Server encountered an error ! message: {message}", extra={"request_number": request_counter})
    addDebugLogToRequest()

def addInfoLog(logger, message):
    global request_counter
    logger.info(message, extra={"request_number": request_counter})

def addDebugLog(logger, message):
    global request_counter
    logger.debug(message, extra={"request_number": request_counter})



######################################################################################################
#                               functions to help implement                                          #
######################################################################################################


#private
def getLog(logger_name):
    for log in logs:
        if log.name == logger_name:
            return {"Logger": log}
    return {"Error" : f"No log by the name '{logger_name}'"}

#public
def getLogLevelInUpper(logger_name):
    response = getLog(logger_name)

    if "Error" in response:
        return response

    logger = response["Logger"]
    current_level = logger.getEffectiveLevel()
    level_name = logging.getLevelName(current_level)
    return level_name.upper()

#private
def isValidLevel(level):
    if level.upper() == "ERROR":
        return level.upper()
    if level.upper() == "INFO":
        return level.upper()
    if level.upper() == "DEBUG":
        return level.upper()
    return {"Error": f"Invalid log level '{level}'"}

#public
def updateLogLevel(name_of_logger, level):
    response = getLog(name_of_logger)
    if "Error" in response:
        return response

    logger = response["Logger"]
    new_logger_level = isValidLevel(level)
    if "Error" in new_logger_level:
        return new_logger_level

    logger.setLevel(new_logger_level)
    return getLogLevelInUpper(name_of_logger)