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
            logging.info(f"Executing data wrangling in {TpPicsWrangling.__name__}")

            # Find the tag line elements in the document
            tag_line_elements = doc.find_all("div", id="header")[0].find_all("ul", class_="sectlevel1")[0]
            # Find the tag level elements within the tag line elements
            tag_level_elements = tag_line_elements.find_all("ul", class_="sectlevel1")
            # Store the wrangled data in an ordered dictionary
            cluster_data = OrderedDict()
            # Count the number of missing PICS definitions
            missing_count = 0
            tc_missing_count = 0

            if len(tag_level_elements) > 0:
                # Process tag line elements if they exist
                for s_n_1, tag_sec_1_elements in enumerate(tag_level_elements):
                    # Find the "a" elements within each tag section 1 element
                    tag_sec1_a_elements = tag_sec_1_elements.parent.find_all("a")
                    # Extract the cluster name from the first "a" element
                    cluster_name = tag_sec1_a_elements[0].text

                    if cluster_name not in cluster_data:
                        # Create a new entry in cluster_data if the cluster name doesn't exist
                        cluster_data[cluster_name] = DataPicsPixit()

                    # Flag to track if a PICS definition is found in the cluster
                    is_pics_found = False
                    is_tc_found = False

                    for a_tag_element in tag_sec1_a_elements:
                        # Extract the heading number and heading name using the TagSeparator class
                        heading_no, heading_name = TagSeparator.separate_tag(a_tag_element.text)

                        if heading_name is None:
                            continue

                        if heading_name == Heading.PICS_DEFINITION.value:
                            # Append the heading number to the PICS ID list
                            cluster_data[cluster_name].pics_id_list.append(heading_no)
                            is_pics_found = True
                        elif heading_name == Heading.PIXIT_DEFINITION.value:
                            # Append the heading number to the PIXIT ID list
                            cluster_data[cluster_name].pixit_id_list.append(heading_no)
                        elif heading_name == Heading.TEST_CASES.value:
                            # Append the heading number to the Test Cases list
                            cluster_data[cluster_name].test_cases_list.append(heading_no)
                            is_tc_found = True

                    if not is_pics_found:
                        # Increment the missing count and log the missing PICS definition
                        missing_count += 1
                        logging.debug(f"PICS definition heading is missing :   {test_plan}-{missing_count}.{cluster_name}")
                    if not is_tc_found:
                        # Increment the missing count and log the missing Test Cases definition
                        tc_missing_count += 1
                        logging.debug(f"Test Cases definition heading is missing :   {test_plan}-{tc_missing_count}.{cluster_name}")

                # Log the total number of missing PICS definitions
                logging.debug(f"No of PICS definition heading is missing :  {test_plan}-{missing_count}")
                logging.debug(f"No of Test Cases definition heading is missing :  {test_plan}-{tc_missing_count}")

            return cluster_data

        except Exception as error:
            # Log the exception details as an error
            logging.exception(f"Error in wrangle_data of {TpPicsWrangling.wrangle_data}: {str(error)}")
            return False
