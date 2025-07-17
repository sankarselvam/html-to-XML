import logging
import os
import datetime
import random
import inspect

class LoggerMixin:
    @staticmethod
    def configure_logging(log_directory='debug', log_file_name='debug_log.log'):
        """
        Configures the logging settings.

        :param log_directory: Directory where log file will be stored.
        :param log_file_name: Name of the log file.
        """
        os.makedirs(log_directory, exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=os.path.join(log_directory, log_file_name)
        )

    @staticmethod
    def log_execution_start(random_id_hex):
        """
        Logs the start of the execution with a unique ID.

        :param random_id_hex: A unique hexadecimal ID for the execution.
        """
        current_time = datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]
        logging.info(
            f"Execution started - Test plan HTML to XML, ID:{random_id_hex} - {datetime.date.today()} - {current_time}")

    @staticmethod
    def log_class_method():
        """
        Logs the current class and method names.
        """
        frame = inspect.currentframe()
        class_name = inspect.getframeinfo(frame).filename
        method_name = inspect.getframeinfo(frame).function
        logging.info(f"Executing {method_name} in {class_name}")

    @staticmethod
    def log_execution_completed(random_id_hex):
        """
        Logs the completion of the execution with a unique ID.

        :param random_id_hex: A unique hexadecimal ID for the execution.
        """
        current_time = datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]
        logging.info(f"Execution Completed: ID:{random_id_hex} - {datetime.date.today()} - {current_time} \n")

    @staticmethod
    def log_execution_terminated(random_id_hex, error=None):
        """
        Logs an unexpected termination of the execution.

        :param random_id_hex: A unique hexadecimal ID for the execution.
        :param error: Optional exception object for logging error details.
        """
        current_time = datetime.datetime.now().strftime("%H:%M:%S:%f")[:-3]
        if error:
            logging.error(f"Execution terminated unexpectedly: ID:{random_id_hex}, Error:\n {str(error)}\n")
        else:
            logging.error(f"Execution terminated unexpectedly: ID:{random_id_hex} - {datetime.date.today()} - {current_time} \n")

    @staticmethod
    def log_error_with_traceback(message, error):
        """
        Logs an error message with traceback.

        :param message: A descriptive message about the error.
        :param error: The exception object that was raised.
        """
        logging.error(message)
        logging.error(f"Error message: {error}")
        logging.error("Traceback:", exc_info=True)
