import logging
import os
from collections import OrderedDict
from bs4 import BeautifulSoup


class HTMLDataAcquisition:
    """
    This class is responsible for acquiring data from HTML files.

    Attributes:
        directory_path (str): The path to the file directory.
        html_files_info (dict): A dictionary containing information about HTML files.
    """

    def __init__(self):
        """
        Initializes a new instance of the HTMLDataAcquisition class.
        """
        self.directory_path = None
        self.html_files_info = None

    def acquire_data(self, directory_path, html_files_info):
        """
        Acquires data from HTML files and returns a dictionary containing the parsed HTML data.

        Args:
            directory_path (str): The path to the file directory.
            html_files_info (dict): A dictionary containing information about HTML files.

        Returns:
            OrderedDict: A dictionary containing the parsed HTML data.
        """

        try:
            # Get the class name and method name for logging
            class_name = self.__class__.__name__
            method_name = "acquire_data"
            logging.info(f"Executing {method_name} in {class_name}")

            # Create an ordered dictionary to store the parsed HTML data
            parsed_html_dict = OrderedDict()

            # Iterate over the HTML files and parse them
            for doc_type, doc_info in html_files_info.items():
                # Get the absolute file path
                file_abs_path = os.path.join(directory_path, doc_info["FileName"])

                # Open the file and parse the HTML
                with open(file_abs_path, encoding="utf8") as file:
                    soup = BeautifulSoup(file, "html.parser")
                    parsed_html_dict[doc_type] = soup
                    #parsed_html_dict[doc_info["PlanName"]] = soup

            # Return the parsed HTML data
            return parsed_html_dict

        except Exception as error:
            logging.exception(f"Error in acquire_data method of HTMLDataAcquisition class: {str(error)}")
            return False
