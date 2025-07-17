import os
import logging
import json


class GenarateTopLevelPics:
    def __init__(self, output_file_name, JsonFilePath):
        self.output_file_name = output_file_name
        self.JsonFilePath = JsonFilePath

    def generate_json(self, data):
        try:
            # directory = os.path.dirname(self.JsonFilePath)
            output_directory = os.path.join(self.JsonFilePath, "OutputJson")
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            output_path = os.path.join(output_directory, self.output_file_name)
            with open(output_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as error:
            logging.exception(f"Error in generate_json of {GenarateTopLevelPics.__name__}: {str(error)}")
            return False
