import json
import json
import logging
import re
from collections import OrderedDict

from tag_separator import TagSeparator
from tp_data_classes import TestCaseData


class TpTestCasesExplorer:
    cluster_data = OrderedDict()
    all_tc_data = OrderedDict()
    top_level_pics = OrderedDict()
    cluster_top_level_data = OrderedDict()
    reference_id_top_level_pics = OrderedDict()

    def explore(self, pics_pixit_test_cases_id, all_tag_data, html_info_dict):
        try:

            logging.info(f"Executing explore in {self.__class__.__name__}")
            # Iterate over each plan and cluster in the pics_pixit_id dictionary
            for plan_name in pics_pixit_test_cases_id:
                if plan_name not in self.all_tc_data:
                    self.all_tc_data[plan_name] = OrderedDict()
                for cluster in pics_pixit_test_cases_id[plan_name]:
                    if cluster not in self.all_tc_data[plan_name]:
                        self.all_tc_data[plan_name][cluster] = OrderedDict()
                    if cluster not in self.cluster_top_level_data:
                        self.cluster_top_level_data[cluster] = []

                    # Get the HTML tag data for the current plan
                    html_tag_data = all_tag_data[plan_name]

                    # Extract the PICS IDs for the current cluster
                    test_cases_list = pics_pixit_test_cases_id[plan_name][cluster].test_cases_list
                    if test_cases_list:
                        return_data = self.load_test_cases_details(test_cases_list[0], html_tag_data, plan_name,
                                                                   cluster, html_info_dict)
                        if return_data is False:
                            # Handle the false condition here
                            logging.debug(
                                f"{cluster}-Test ID- Return False-Error in {TpTestCasesExplorer.__name__}:{test_cases_list[0]} ")
                            continue
                        else:
                            tc_dict, top_level_pics_list = return_data
                            self.all_tc_data[plan_name][cluster] = tc_dict
                            self.cluster_top_level_data[cluster] = top_level_pics_list
                    else:
                        logging.debug(f"No Test Cases in   :  {cluster}")

            with open('top_level.json', 'w') as file:
                # Write the JSON data to the file
                json.dump(self.top_level_pics, file)
            return self.all_tc_data, self.top_level_pics, self.cluster_top_level_data, self.reference_id_top_level_pics

        except Exception as error:
            # Log the exception details as an error
            logging.exception(f"Error in explore of {TpTestCasesExplorer.__name__}: {str(error)}")
            return False

    def load_test_cases_details(self, test_cases_id, html_tag_data, plan_name, cluster, html_info_dict):
        try:
            tc_dict = OrderedDict()
            cluster_top_level_pics = []
            tag_pic = html_tag_data[test_cases_id].doc
            sect2_list = tag_pic.find_all('div', class_="sect2")
            '''
            for sect1 in sect1_list:
                sect2_list = sect1.find_all('div', class_="sect2")
                h2_element = sect1.find('h2')
                test_text = h2_element.text
                logging.debug(f"TC-Cluster Heading-{cluster}-{test_text} ")
            '''
            for sect2 in sect2_list:
                sect3_list = sect2.find_all('div', class_="sect3")
                h3_element = sect2.find('h3')
                type_text = h3_element.text
                test_type_id, test_type_name = TagSeparator.separate_tag(type_text)
                # logging.debug(f"TC-Type Heading-{cluster}-{type_text} ")
                if test_type_name not in tc_dict:
                    tc_dict[test_type_name] = OrderedDict()

                for sect3 in sect3_list:
                    h4_element = sect3.find('h4')
                    test_name_text = h4_element.text
                    test_tag_id, test_case_full_name = TagSeparator.separate_tag(test_name_text)
                    # Extract the test ID
                    start_index = test_case_full_name.find('[') + 1
                    end_index = test_case_full_name.find(']')
                    test_id = test_case_full_name[start_index:end_index]

                    # Extract the test name
                    test_name = test_case_full_name[end_index + 2:]
                    # tag_pic_with_name.text+ " - "+doc_name
                    # doc_name=html_info_dict[plan_name]['DocumentName']
                    obj_test_case_data = TestCaseData(plan_name, cluster, test_type_name, test_id, test_name,
                                                      test_case_full_name, test_tag_id)
                    if test_id not in tc_dict[test_type_name]:
                        tc_dict[test_type_name][test_id] = obj_test_case_data
                    else:
                        logging.debug(f"Duplicate Test ID Found-{cluster}-{test_type_name}-{test_id}-{test_name} ")

                    # logging.debug(f"TC-Name Heading-{cluster}-{test_type_name}-{test_id}-{test_name} ")
                    debug_message = f"TC-PICS Details-{cluster}-{test_id}-"
                    sect4_list = sect3.find_all('div', class_="sect4")
                    for sect4 in sect4_list:

                        h5_tag = sect4.find('h5')
                        if h5_tag and h5_tag.text == "PICS":
                            top_pics = []
                            ul_tag = sect4.find('div', class_="ulist")
                            if ul_tag:
                                li_tags = ul_tag.find_all('li')
                                for idx, li_tag in enumerate(li_tags, start=1):
                                    p_tag = li_tag.find('p')
                                    pics_text = p_tag.text
                                    # Extract the desired part before the parentheses
                                    pics_name = re.sub(r'\([^)]*\)', '', pics_text)
                                    top_pics.append(pics_name)
                                    if pics_name not in cluster_top_level_pics:
                                        cluster_top_level_pics.append(pics_name)
                                    # tag_pic_with_name.text+ " - "+doc_name
                                    doc_name = html_info_dict[plan_name]['DocumentName']
                                    if pics_name not in self.reference_id_top_level_pics:
                                        self.reference_id_top_level_pics[pics_name] = test_name_text + " - " + doc_name

                                    # logging.debug(f"{debug_message} {idx}.{pics_name}")
                            else:
                                logging.debug(f"{debug_message} No Top PICS found.")
                            self.top_level_pics[test_id] = top_pics
                            break

            return tc_dict, cluster_top_level_pics
        except Exception as error:
            logging.exception(f"Error in load_pics_tag of {TpTestCasesExplorer.__name__}: {str(error)}")
            return False
