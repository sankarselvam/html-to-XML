import logging

from create_cluster_xml_files import CreateClusterXmlFiles
from genarate_top_level_pics_json import GenarateTopLevelPics
from html_data_acquisition import HTMLDataAcquisition
from json_test_plan_reader import JsonTestPlanReader
from revision_html_data import RevisionHtmlData
from html_data_wrangler import HTMLDataWrangler
from status_finder import StatusFinder
from tp_pics_explorer import TpPicsExplorer
from tp_test_cases_explorer import TpTestCasesExplorer
from xml_pics_exploration import XmlPicsExploration


class DataProcessor:
    @staticmethod
    def process_data(debug=False):
        """
        Executes the data processing.

        Args:
            debug (bool): Specifies if debug mode is enabled. Default is False.

        Returns:
            bool: True if the data is processed successfully, False otherwise.
        """

        try:
            class_name = DataProcessor.__name__
            method_name = "process_data"
            logging.info(f"Executing {method_name} in {class_name}")

            # Create an instance of JsonTestPlanReader
            json_reader = JsonTestPlanReader()
            # Specify the JSON file name
            json_file_name = "ConfigXmlTp.json"
            # Read and process data from the JSON file
            is_data_processed = json_reader.read_file_data(json_file_name)
            if not is_data_processed:
                # Log the error if data processing fails
                logging.error(f'process_data in {class_name}:failed to read or process JSON file')
                return False

            # Create an instance of HTMLDataAcquisition
            html_acquirer = HTMLDataAcquisition()
            # Acquire HTML data
            soup_data = html_acquirer.acquire_data(json_reader.file_path, json_reader.html_files)
            if not soup_data:
                # Log the error if HTML data acquisition fails
                logging.error(f'process_data in {class_name}: failed to acquire HTML data')
                return False

            # Create an instance of RevisionHtmlData
            revision_data = RevisionHtmlData()
            # Explore data
            rev_data = revision_data.extract_revision_data(soup_data)
            if not rev_data:
                # Log the error if data exploration fails
                logging.error(f'process_data in {class_name}: failed to explore data')
                return False

            # Process HTML data using HTMLDataWrangler
            html_processing_result = HTMLDataWrangler.process_html_data(soup_data)
            if not html_processing_result:
                # Log the error if HTML data processing fails
                logging.error(f'process_data in {class_name}: failed to process HTML data')
                return False
            else:
                try:
                    tag_html, pics_pixit_id = html_processing_result
                except ValueError:
                    # Log the error if the format of html_processing_result is incorrect
                    logging.error(f'process_data in {class_name}: invalid html_processing_result format')
                    return False

            # Loading pics,pixit table data
            obj_pics_exploration = TpPicsExplorer()
            pics_pixit_table_data = obj_pics_exploration.explore(pics_pixit_id, tag_html, json_reader.html_files)
            if not pics_pixit_table_data:
                # Log the error if HTML data processing fails
                logging.error(f'Tp PICS explore in {class_name}: failed to get pics,pixit table data')
                return False

            # Loading Test case,PICS  details
            obj_test_cases_exploration = TpTestCasesExplorer()
            return_test_cases_data = obj_test_cases_exploration.explore(pics_pixit_id, tag_html, json_reader.html_files)
            if not return_test_cases_data:
                # Log the error if HTML data processing fails
                logging.error(f'Test cases explore in {class_name}: failed to get test cases and top level PICS')
                return False
            else:
                try:
                    all_tc_data, top_level_pics, cluster_top_level_data, reference_tl_pics = return_test_cases_data
                except ValueError:
                    # Log the error if the number of elements in return_test_cases_data is incorrect
                    logging.error(f'{method_name} in {class_name}: invalid return_test_cases_data format')
                    return False

            # Writing Top Level PICS JSON file
            json_writer = GenarateTopLevelPics(json_reader.top_level_json_name, json_reader.xml_path)
            return_json_writer = json_writer.generate_json(top_level_pics)
            if not return_json_writer:
                # Log the error if HTML data processing fails
                logging.error(f'process_data in {class_name}: failed to write Top Level PICS JSON file')
                return False

            # Reading all the pics,pixit table data
            obj_xml_pics = XmlPicsExploration()
            return_xml_data = obj_xml_pics.exploration(pics_pixit_table_data, cluster_top_level_data, reference_tl_pics)
            if not return_xml_data:
                # Log the error if HTML data processing fails
                logging.error(f'process_data in {class_name}: failed to get xml PICS data')
                return False
            else:
                try:
                    xml_data, mcore_cluster_list, combined_pics_list = return_xml_data
                except ValueError:
                    # Log the error if the number of elements in return_test_cases_data is incorrect
                    logging.error(f'{method_name} in {class_name}: invalid return_xml_data format')
                    return False
            # Writing conformance values and status condition
            obj_status_finder = StatusFinder()
            updated_xml_data = obj_status_finder.process_cluster_data(xml_data)
            if not updated_xml_data:
                # Log the error if HTML data processing fails
                logging.error(f'process_data in {class_name}: failed to get Conformance values and condition')
                return False

            # Create an instance of CreateClusterXmlFiles
            cluster_xml = CreateClusterXmlFiles(
                xml_data,
                rev_data,
                json_reader.xml_path,
                mcore_cluster_list,
                combined_pics_list,
                json_reader.version_name
            )
            # Call the write_file method to generate the XML files
            cluster_xml.write_file()

            return True

        except Exception as error:
            # Log the exception details as an error
            logging.exception(f"Error in process_data of {DataProcessor.__name__}: {str(error)}")
            return False
