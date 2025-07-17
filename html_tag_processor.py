import logging
from collections import OrderedDict
from tag_separator import TagSeparator
from tp_data_classes import DataTag


class HtmlTagProcessor:
    def __init__(self):
        """
        Initializes an instance of HtmlTagProcessor class.
        """
        try:
            self.count = 1
            self.loop_dict = OrderedDict()
        except Exception as error:
            class_name = self.__class__.__name__
            method_name = "__init__"
            logging.exception(f"Error in {class_name} of {method_name}: {str(error)}")

    def process_html_data(self, soup_html_dict):
        """
        Processes the HTML data and returns all tag data as a dictionary.

        Args:
            soup_html_dict (dict): A dictionary containing the HTML data.

        Returns:
            dict: A dictionary containing all the tag data.
        """
        try:
            class_name = self.__class__.__name__
            method_name = "process_html_data"
            logging.info(f"Executing {method_name} in {class_name}")
            all_tag_dict = self.load_html(soup_html_dict)
            return all_tag_dict
        except Exception as error:
            class_name = self.__class__.__name__
            method_name = "process_html_data"
            logging.exception(f"Error in {class_name} of {method_name}: {str(error)}")

    def load_html(self, html_dict):
        """
        Loads the HTML data and extracts all the tag data.

        Args:
            html_dict (dict): A dictionary containing the HTML data.

        Returns:
            dict: A dictionary containing all the tag data.
        """
        try:
            class_name = self.__class__.__name__
            method_name = "load_html"
            logging.info(f"Executing {method_name} in {class_name}")
            obj_data = DataTag(1, html_dict)
            self.loop_dict = OrderedDict()
            self.extract_tag_data(obj_data)
            all_tag_data = self.loop_dict
            return all_tag_data
        except Exception as error:
            class_name = self.__class__.__name__
            method_name = "load_html"
            logging.exception(f"Error in {class_name} of {method_name}: {str(error)}")

    def extract_tag_data(self, obj_data):
        """
        Recursively retrieves the HTML data and extracts tag data.

        Args:
            obj_data (DataTag): An instance of DataTag class containing the HTML data.
        """
        try:
            obj_ret_value = self.find_section_details(obj_data)
            found_count = len(obj_ret_value.doc)
            if found_count > 0:
                for obj_doc_next in obj_ret_value.doc:
                    obj_data_tag = DataTag(obj_ret_value.value, obj_doc_next)
                    self.count += 1
                    id_obj = self.get_id_doc_data(obj_data_tag)
                    if id_obj.id is not None:
                        if id_obj.id not in self.loop_dict:
                            self.loop_dict[id_obj.id] = id_obj
                    self.extract_tag_data(obj_data_tag)
        except Exception as error:
            class_name = self.__class__.__name__
            method_name = "extract_tag_data"
            logging.exception(f"Error in {class_name} of {method_name}: {str(error)}")

    @staticmethod
    def find_section_details(obj_data):
        """
        Finds and retrieves the details of a specific section in the HTML.

        Args:
            obj_data (DataTag): An instance of DataTag class containing the HTML data.

        Returns:
            DataTag: An instance of DataTag class containing the section details.
        """
        try:
            obj_data_tag = DataTag(obj_data.value + 1)
            sec_str = "sect" + str(obj_data.value)
            obj_data_tag.doc = obj_data.doc.find_all("div", class_=sec_str)
            if len(obj_data_tag.doc) > 0:
                h_str = "h" + str(obj_data.value + 1)
                text_level_1 = obj_data.doc.find_all(h_str)[0].text
                obj_data_tag.id, obj_data_tag.name = TagSeparator.separate_tag(text_level_1)
            return obj_data_tag
        except Exception as error:
            class_name = HtmlTagProcessor.__name__
            method_name = "find_section_details"
            logging.exception(f"Error in {method_name} of {class_name}: {str(error)}")

    @staticmethod
    def get_id_doc_data(obj_data):
        """
        Retrieves the ID and document data from the given object.

        Args:
            obj_data (DataTag): An instance of DataTag class containing the document data.

        Returns:
            DataTag: An instance of DataTag class containing the ID and document data.
        """
        try:
            obj_data_tag = DataTag(obj_data.value, obj_data.doc)
            h_str = "h" + str(obj_data.value)
            text_level_1 = obj_data.doc.find_all(h_str)[0].text
            obj_data_tag.id, obj_data_tag.name = TagSeparator.separate_tag(text_level_1)
            return obj_data_tag
        except Exception as error:
            class_name = HtmlTagProcessor.__name__
            method_name = "get_id_doc_data"
            logging.exception(f"Error in {method_name} of {class_name}: {str(error)}")
