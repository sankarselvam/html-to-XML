import logging
from collections import OrderedDict

from tag_separator import TagSeparator
from tp_data_classes import DataPicsPixit, Heading


class TpPicsWrangling:
    """
    Class for wrangling TP pics data.
    """

    @staticmethod
    def wrangle_data(doc, test_plan):
        """
        Extracts and wrangles TP pics data from the provided document.

        Args:
            doc (BeautifulSoup): The BeautifulSoup document object.
            test_plan (str): The test plan.

        Returns:
            OrderedDict: Cluster data containing the wrangled TP pics data.
        """
        try:
            # Log the start of data wrangling
            logging.info(f"Starting wrangle_data method in {TpPicsWrangling.__name__} for test_plan: {test_plan}")
            logging.debug(f"Input parameters - doc type: {type(doc)}, test_plan: {test_plan}")

            # Find the tag line elements in the document
            logging.debug("Searching for tag line elements in document")
            tag_line_elements = doc.find_all("div", id="header")[0].find_all("ul", class_="sectlevel1")[0]
            logging.debug(f"Found tag_line_elements: {type(tag_line_elements)}")
            
            # Find the tag level elements within the tag line elements
            tag_level_elements = tag_line_elements.find_all("ul", class_="sectlevel1")
            logging.debug(f"Found {len(tag_level_elements)} tag_level_elements")
            
            # Store the wrangled data in an ordered dictionary
            cluster_data = OrderedDict()
            logging.debug("Initialized cluster_data OrderedDict")
            
            # Count the number of missing PICS definitions
            missing_count = 0
            tc_missing_count = 0
            logging.debug("Initialized missing_count and tc_missing_count to 0")

            if len(tag_level_elements) > 0:
                logging.debug(f"Processing {len(tag_level_elements)} tag_level_elements")
                # Process tag line elements if they exist
                for s_n_1, tag_sec_1_elements in enumerate(tag_level_elements):
                    logging.debug(f"Processing tag_sec_1_elements {s_n_1 + 1}/{len(tag_level_elements)}")
                    
                    # Find the "a" elements within each tag section 1 element
                    tag_sec1_a_elements = tag_sec_1_elements.parent.find_all("a")
                    logging.debug(f"Found {len(tag_sec1_a_elements)} 'a' elements in current tag section")
                    
                    # Extract the cluster name from the first "a" element
                    cluster_name = tag_sec1_a_elements[0].text
                    logging.debug(f"Extracted cluster_name: '{cluster_name}'")

                    if cluster_name not in cluster_data:
                        # Create a new entry in cluster_data if the cluster name doesn't exist
                        logging.debug(f"Creating new cluster entry for: '{cluster_name}'")
                        cluster_data[cluster_name] = DataPicsPixit()
                    else:
                        logging.debug(f"Cluster '{cluster_name}' already exists in cluster_data")

                    # Flag to track if a PICS definition is found in the cluster
                    is_pics_found = False
                    is_tc_found = False
                    logging.debug(f"Initialized flags - is_pics_found: {is_pics_found}, is_tc_found: {is_tc_found}")

                    for a_tag_element in tag_sec1_a_elements:
                        # Extract the heading number and heading name using the TagSeparator class
                        heading_no, heading_name = TagSeparator.separate_tag(a_tag_element.text)
                        logging.debug(f"Processed tag: '{a_tag_element.text}' -> heading_no: '{heading_no}', heading_name: '{heading_name}'")

                        if heading_name is None:
                            logging.debug("Skipping element with None heading_name")
                            continue

                        if heading_name == Heading.PICS_DEFINITION.value:
                            # Append the heading number to the PICS ID list
                            logging.debug(f"Found PICS Definition - adding heading_no '{heading_no}' to pics_id_list")
                            cluster_data[cluster_name].pics_id_list.append(heading_no)
                            is_pics_found = True
                            logging.debug(f"Updated is_pics_found to: {is_pics_found}")
                        elif heading_name == Heading.PIXIT_DEFINITION.value:
                            # Append the heading number to the PIXIT ID list
                            logging.debug(f"Found PIXIT Definition - adding heading_no '{heading_no}' to pixit_id_list")
                            cluster_data[cluster_name].pixit_id_list.append(heading_no)
                        elif heading_name == Heading.TEST_CASES.value:
                            # Append the heading number to the Test Cases list
                            logging.debug(f"Found Test Cases - adding heading_no '{heading_no}' to test_cases_list")
                            cluster_data[cluster_name].test_cases_list.append(heading_no)
                            is_tc_found = True
                            logging.debug(f"Updated is_tc_found to: {is_tc_found}")
                        else:
                            logging.debug(f"Unrecognized heading_name: '{heading_name}' - no action taken")

                    if not is_pics_found:
                        # Increment the missing count and log the missing PICS definition
                        missing_count += 1
                        logging.debug(f"PICS definition heading is missing :   {test_plan}-{missing_count}.{cluster_name}")
                        logging.debug(f"Updated missing_count to: {missing_count}")
                    if not is_tc_found:
                        # Increment the missing count and log the missing Test Cases definition
                        tc_missing_count += 1
                        logging.debug(f"Test Cases definition heading is missing :   {test_plan}-{tc_missing_count}.{cluster_name}")
                        logging.debug(f"Updated tc_missing_count to: {tc_missing_count}")
                    
                    # Log current cluster processing completion
                    logging.debug(f"Completed processing cluster '{cluster_name}' - PICS found: {is_pics_found}, TC found: {is_tc_found}")
                    logging.debug(f"Current cluster_data for '{cluster_name}': PICS IDs: {len(cluster_data[cluster_name].pics_id_list)}, "
                                f"PIXIT IDs: {len(cluster_data[cluster_name].pixit_id_list)}, "
                                f"Test Cases: {len(cluster_data[cluster_name].test_cases_list)}")

                # Log the total number of missing PICS definitions
                logging.debug(f"No of PICS definition heading is missing :  {test_plan}-{missing_count}")
                logging.debug(f"No of Test Cases definition heading is missing :  {test_plan}-{tc_missing_count}")
                logging.debug(f"Processing completed for all {len(tag_level_elements)} clusters")
            else:
                logging.debug("No tag_level_elements found - skipping processing")

            # Log final summary
            total_clusters = len(cluster_data)
            logging.debug(f"Final cluster_data summary: {total_clusters} clusters processed")
            for cluster_name, data in cluster_data.items():
                logging.debug(f"Cluster '{cluster_name}': {len(data.pics_id_list)} PICS, "
                            f"{len(data.pixit_id_list)} PIXIT, {len(data.test_cases_list)} Test Cases")
            
            logging.info(f"wrangle_data completed successfully for test_plan: {test_plan}, "
                        f"processed {total_clusters} clusters, missing PICS: {missing_count}, missing TC: {tc_missing_count}")

            return cluster_data

        except Exception as error:
            # Log the exception details as an error
            logging.exception(f"Error in wrangle_data of {TpPicsWrangling.wrangle_data}: {str(error)}")
            return False
