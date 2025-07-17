
import random
from data_processor import DataProcessor
from logger_mixin import LoggerMixin


def main():
    """
    Executes the test plan for converting HTML to XML and logs the execution details.
    """
    random_id_hex = format(random.randint(0, 16777215), '06X')

    try:
        # Configure logging
        LoggerMixin.configure_logging()

        # Log the execution start
        LoggerMixin.log_execution_start(random_id_hex)

        # Log class and method names
        LoggerMixin.log_class_method()

        print("Start")

        # Execute the process_data function
        return_status = DataProcessor.process_data(True)

        if return_status:
            # Log the completion
            LoggerMixin.log_execution_completed(random_id_hex)
            print("# Completed #")
        else:
            # Log the unexpected termination
            LoggerMixin.log_execution_terminated(random_id_hex)
            print("# Execution terminated #")

        print("End")

    except Exception as error:
        # Log the exception details
        LoggerMixin.log_execution_terminated(random_id_hex, error)


if __name__ == "__main__":
    main()
