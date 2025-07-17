import inspect
import json
import logging
import os
from os import path


class JsonTestPlanReader:
    """
    This class is responsible for reading data from a JSON file.

    Attributes:
        file_path (str): The file location.
        html_files (dict): The HTML files for test plans.
        xml_path (str): The XML file path.
        version_name (str): The version name.
        top_level_json_name (str): The top-level JSON name.
        combined_file_name (str): The combined file name of top_level_json_name and version_name.
    """

    def __init__(self):
        """
        Initializes a new instance of the JsonTestPlanReader class.
        """
        self.file_path = None
        self.html_files = None
        self.xml_path = None
        self.version_name = None
        self.top_level_json_name = None
        self.combined_file_name = None

    def read_file_data(self, json_file_name):
        """
        Reads data from a JSON file and populates the attributes.

        Args:
            json_file_name (str): The name of the JSON file to read.

        Returns:
            bool: True if the file is successfully read, False otherwise.
        """

        try:
            class_name = self.__class__.__name__
            logging.info(f"Executing {inspect.currentframe().f_code.co_name} in {class_name}")

            # Get the base path of the current file
            base_path = os.path.dirname(os.path.abspath(__file__))

            # Construct the path to the JSON file
            json_file_path = os.path.join(base_path, json_file_name)

            if path.exists(json_file_path):
                # Read and parse the JSON file
                with open(json_file_path) as file:
                    config_data_dict = json.load(file)

                # Populate the attributes with the data from the JSON file
                self.file_path = config_data_dict.get("FileLocation")
                self.html_files = config_data_dict.get("TestPlanHtmlFiles")
                self.xml_path = config_data_dict.get("XmlFilePath")
                self.version_name = config_data_dict.get("VersionName")
                self.top_level_json_name = config_data_dict.get("TopLevelJsonName") + "_" + self.version_name+".json"

                return True
            else:
                print(json_file_name + " file is not found")
                return False
        except Exception as error:
            current_method_name = inspect.currentframe().f_code.co_name
            error_class_name = self.__class__.__name__
            logging.exception(f"Error in {current_method_name} of {error_class_name}: {str(error)}")
            return False
