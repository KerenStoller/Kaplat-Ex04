######################################################################################################
#                                   logger creation                                                  #
######################################################################################################
import logging
import time
import os
import sys
import atexit

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # If the app is bundled via PyInstaller
        return os.path.dirname(sys.executable)
    else:
        # If running as a normal script
        return os.path.dirname(os.path.abspath(__file__))


class LoggerManager:
    log_format = "%(asctime)s %(levelname)s: %(message)s | request #%(request_number)s "
    date_format = "%d-%m-%Y %H:%M:%S"

    def __init__(self):
        self.formatter = logging.Formatter(self.log_format, datefmt=self.date_format)
        self.request_counter = 0
        self.request_start_time = 0
        self.all_logs_path = os.path.join(get_base_dir(), "logs")
        os.makedirs(self.all_logs_path, exist_ok=True)
        self.request_logger = self.create_logger("request-logger", "requests.log", logging.INFO, True)
        self.stack_logger = self.create_logger("stack-logger", "stack.log", logging.INFO)
        self.independent_logger = self.create_logger("independent-logger", "independent.log", logging.DEBUG)
        self.logs = [self.request_logger, self.stack_logger, self.independent_logger]
        # Register shutdown handler to flush and close handlers
        atexit.register(self.close_handlers)

    def close_handlers(self):
        for logger in self.logs:
            for handler in logger.handlers:
                handler.flush()
                handler.close()

    def create_logger(self, name, log_file, level=logging.INFO, to_console=False):
        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.setLevel(level)
            logger.propagate = False

            log_path = os.path.join(self.all_logs_path, log_file)
            file_handler = logging.FileHandler(log_path, mode='a')
            file_handler.setFormatter(self.formatter)
            logger.addHandler(file_handler)

            if to_console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(self.formatter)
                logger.addHandler(console_handler)

        return logger

    ######################################################################################################
    #                               logging methods                                                      #
    ######################################################################################################

    def add_info_log_to_request(self, resource_name, http_verb):
        self.request_start_time = time.perf_counter()
        self.request_counter += 1
        log_details = f"Incoming request | #{self.request_counter} | resource: {resource_name} | HTTP Verb {http_verb.upper()}"
        self.request_logger.info(log_details, extra={"request_number": self.request_counter})

    def add_debug_log_to_request(self):
        duration = (time.perf_counter() - self.request_start_time) * 1000  # ms
        duration = round(duration, 1)
        log_details = f"request #{self.request_counter} duration: {duration:.1f}ms"
        self.request_logger.debug(log_details, extra={"request_number": self.request_counter})

    def add_error_log(self, logger, message):
        logger.error(f"Server encountered an error ! message: {message}",
                     extra={"request_number": self.request_counter})
        self.add_debug_log_to_request()

    def add_info_log(self, logger, message):
        logger.info(message, extra={"request_number": self.request_counter})

    def add_debug_log(self, logger, message):
        logger.debug(message, extra={"request_number": self.request_counter})

    ######################################################################################################
    #                               functions to help implement                                          #
    ######################################################################################################
    def get_log(self, logger_name):
        for log in self.logs:
            if log.name == logger_name:
                return {"Logger": log}
        return {"Error": f"No log by the name '{logger_name}'"}

    def get_log_level_in_upper(self, logger_name):
        response = self.get_log(logger_name)
        if "Error" in response:
            return response

        logger = response["Logger"]
        current_level = logger.getEffectiveLevel()
        level_name = logging.getLevelName(current_level)
        return level_name.upper()

    def is_valid_level(self, level):
        if level.upper() in {"ERROR", "INFO", "DEBUG"}:
            return level.upper()
        return {"Error": f"Invalid log level '{level}'"}

    def update_log_level(self, name_of_logger, level):
        response = self.get_log(name_of_logger)
        if "Error" in response:
            return response

        logger = response["Logger"]
        new_logger_level = self.is_valid_level(level)
        if "Error" in new_logger_level:
            return new_logger_level

        logger.setLevel(new_logger_level)
        return self.get_log_level_in_upper(name_of_logger)
