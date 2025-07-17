import logging
from collections import OrderedDict

from html_tag_processor import HtmlTagProcessor
from tp_pics_wrangling import TpPicsWrangling


class HTMLDataWrangler:
    @staticmethod
    def process_html_data(html_data_dict):
        """
        Perform dictionary tag wrangling on the given HTML data.

        Args:
            html_data_dict (dict): Dictionary containing HTML data for test cases.

        Returns:
            tuple: A tuple containing the processed tag data and picture IDs.

        """
        try:
            logging.info(f"Executing process_html_data in {HTMLDataWrangler.__name__}")

            html_tag_processor = HtmlTagProcessor()
            processed_tag_data = OrderedDict()
            pic_pixit_tc_id = OrderedDict()

            for test_plan, html_data in html_data_dict.items():
                processed_tag_data[test_plan] = html_tag_processor.process_html_data(html_data)
                pic_pixit_tc_id[test_plan] = TpPicsWrangling.wrangle_data(html_data, test_plan)

            logging.info(f"process_html_data in {HTMLDataWrangler.__name__} executed successfully")
            return processed_tag_data, pic_pixit_tc_id
        except Exception as error:
            logging.exception(f"Error in process_html_data of {HTMLDataWrangler.__name__}: {str(error)}")
            return False
