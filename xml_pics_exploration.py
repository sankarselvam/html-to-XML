import logging
import re
from collections import OrderedDict
from typing import Tuple
import copy

import pandas as pd

from logger_mixin import LoggerMixin
from tp_data_classes import XmlData, PicsXmlData, PicsDetails, AllTypePics, AllClusterSide, ServerClient, \
    ClusterReference


class XmlPicsExploration(LoggerMixin):
    """
    Class for exploring XML pics data.
    """

    # Region Regex Definitions
    regex_sc_manual = r"^([\w]+)\.([S,C])\.([M])\.([\w]+)"
    regex_attributes = r'^(([\w]+)\.([S,C])\.([A])([0-9a-fA-F]{4}))\(([\w]+)\)$'
    regex_events = r'^(([\w]+)\.([S,C])\.([E])([0-9a-fA-F]{2}))\(([\w]+)\)'
    regex_features = r'^(([\w]+)\.([S,C])\.([F])([0-9a-fA-F]{2}))\(([\w]+)\)'
    regex_attributes_write = r"^(([\w]+)\.([S,C])\.([A])([0-9a-fA-F]{4}))\(([\w]+)\)\.([\w]+)"
    regex_commands = r'^(([\w]+)\.([S,C])\.([C])([0-9a-fA-F]{2})\.(Rsp|Tx))\(([\w\s]+)\)'
    regex_manual = r"^([\w]+)\.([M])\.([\w]+)"
    regex_role = r"^([\w]+)\.([SC])$"
    regex_attributes_extra_dot = r"^(([\w]+)\.([S,C])\.([A])([0-9a-fA-F]{4}))\.(([\w]+)\(([\w]+)\))"
    regex_attributes_spl = r"^(([\w]+)\.([S,C])\.([A])([0-9a-fA-F]{4})\.([\w]+))$"
    regex_mcore = r"^MCORE"

    # Instance variables
    debug_text = "Unexpected PICS Format : "

    def __init__(self):
        self.mcore_pics_list = []
        self.cluster_pics_list = []
        self.test_plan_cluster_pics_dict = OrderedDict()
        self.cluster_pixit_list = []
        self.is_mcore_pics = False
        self.is_other_pics = False
        self.combined_pics_list = []
        self.all_pics_list = []
        self.mcore_cluster_list = []
        self.xml_data = OrderedDict()
        self.all_pics_data = OrderedDict()
        self.missing_top_level_pics = []
        self.missing_top_level_cluster_pics = OrderedDict()
        # Define regex patterns and their associated types
        self.regex_patterns = [
            (self.regex_attributes, AllTypePics.ATTRIBUTES),
            (self.regex_attributes_write, AllTypePics.ATTRIBUTES),
            (self.regex_attributes_extra_dot, AllTypePics.ATTRIBUTES),
            (self.regex_attributes_spl, AllTypePics.ATTRIBUTES),
            (self.regex_commands, AllTypePics.COMMANDS_RECEIVED),
            (self.regex_events, AllTypePics.EVENTS),
            (self.regex_features, AllTypePics.FEATURES),
            (self.regex_sc_manual, AllTypePics.MANUALLY),
            (self.regex_manual, AllTypePics.MANUALLY)
        ]

    # endregion
    def exploration(self, pics_table_data, cluster_top_level_data, reference_tl_pics):
        try:
            logging.info(f"Executing exploration in {self.__class__.__name__}")

            for cluster, data in pics_table_data.items():
                if cluster == "Dishwasher Alarm Cluster Test Plan":
                    a = 1  # Placeholder for any special handling

                obj_xml_pic = XmlData(cluster)
                self.is_mcore_pics = False
                self.is_other_pics = False
                self.cluster_pics_list = []

                pixit_dict = data.pixit_dict
                if pixit_dict:
                    return_obj_xml_pixit = self.process_pixit_table_data(pixit_dict, obj_xml_pic, cluster)
                    if return_obj_xml_pixit is not None:
                        obj_xml_pic = return_obj_xml_pixit
                    else:
                        logging.debug(f"Unable to get data in {cluster}")

                pics_dict = data.pics_dict
                if pics_dict:
                    for parent_heading, child_heading_or_tag_list in pics_dict.items():
                        if isinstance(child_heading_or_tag_list, OrderedDict):
                            for child_heading, tag_list in child_heading_or_tag_list.items():
                                return_obj_xml_pic = self.process_pics_table_data(
                                    tag_list, obj_xml_pic, cluster, parent_heading, child_heading)
                                if return_obj_xml_pic is not None:
                                    obj_xml_pic = return_obj_xml_pic
                                else:
                                    logging.debug(f"Unable to get data in {cluster}")
                        else:
                            if child_heading_or_tag_list is not None:
                                return_obj_xml_pic = self.process_pics_table_data(
                                    child_heading_or_tag_list, obj_xml_pic, cluster, parent_heading)
                                if return_obj_xml_pic is not None:
                                    obj_xml_pic = return_obj_xml_pic
                                else:
                                    logging.debug(f"Unable to get data in {cluster}")

                    if cluster == "Access Control Enforcement Test Plan":
                        a = 1  # Placeholder for any special handling

                    tc_top_level_pics = cluster_top_level_data.get(cluster, [])
                    tc_cluster_difference = [
                        pic for pic in tc_top_level_pics if pic not in self.cluster_pics_list]
                    missing_top_pixit = [
                        pic for pic in tc_cluster_difference if pic not in self.mcore_pics_list]
                    missing_top_pics = [
                        pic for pic in missing_top_pixit if pic not in self.cluster_pixit_list]
                    obj_xml_pic.missing_top_pics = missing_top_pics

                    self.missing_top_level_pics.extend(missing_top_pics)
                    self.missing_top_level_cluster_pics[cluster] = missing_top_pics
                    if self.is_other_pics and self.is_mcore_pics:
                        if cluster not in self.combined_pics_list:
                            self.combined_pics_list.append(cluster)
                        obj_xml_pic.is_both_pics = True

                return_pics_code = self.extract_pics_code_from_role(obj_xml_pic)
                if not return_pics_code:
                    return None
                self.xml_data[cluster] = obj_xml_pic

            return_value = self.update_missing_top_level_cluster_pics_data(reference_tl_pics)

            logging.info("XmlPicsExploration - exploration : End")
            mcore_cluster_str = " ,\n ".join(map(str, self.mcore_cluster_list))
            logging.info("mcore_cluster_list - \n" + mcore_cluster_str)

            return self.xml_data, self.mcore_cluster_list, self.combined_pics_list

        except Exception as error:
            self.log_error_with_traceback(f"Error in exploration of {self.__class__.__name__}", error)
            return False


    def extract_pics_code_from_role(self,obj_xml_pic):
        try:
            # Initialize an empty set to store unique pics_code values
            pics_codes_set = set()

            # Check if the 'role' dictionary is not empty
            if obj_xml_pic.role:
                # Iterate through all the keys in the 'role' dictionary
                for key in obj_xml_pic.role.keys():
                    # Extract the 'pics_code' value from the key and add it to the set
                    pics_code = key.split('.')[0]
                    pics_codes_set.add(pics_code)

            # Update self.pics_code with the list of unique pics_codes
            obj_xml_pic.pics_code = list(pics_codes_set)

            return True
        except Exception as error:
            self.log_error_with_traceback(
                f"Error in extract_pics_code_from_role of {XmlPicsExploration.__name__}", error)
            return False

    def process_pics_table_data(self, tag_list, obj_xml_pic, cluster, parent_heading, child_heading=None):
        try:
            for pics_xml in tag_list:
                if pics_xml.variable is not None:
                    for _id in range(len(pics_xml.variable)):
                        obj_pics_xml_data = self.read_pics_data(pics_xml, _id)
                        if obj_pics_xml_data is not None:
                            return_pic_data = self.process_upload_pics_object(
                                obj_xml_pic, obj_pics_xml_data, cluster, parent_heading, child_heading
                            )
                            if return_pic_data is not None:
                                try:
                                    obj_xml_pic, obj_pics_xml_data, obj_pics_details = return_pic_data
                                    if obj_pics_xml_data.pics not in self.cluster_pics_list:
                                        self.cluster_pics_list.append(obj_pics_xml_data.pics)
                                    if obj_pics_xml_data.pics not in self.test_plan_cluster_pics_dict:
                                        self.test_plan_cluster_pics_dict[obj_pics_xml_data.pics] = []
                                    self.test_plan_cluster_pics_dict[obj_pics_xml_data.pics].append(cluster)
                                    if obj_pics_xml_data.pics not in self.all_pics_list:
                                        self.all_pics_list.append(obj_pics_xml_data.pics)
                                    if obj_pics_xml_data.pics not in self.all_pics_data:
                                        self.all_pics_data[obj_pics_xml_data.pics] = obj_pics_details
                                except ValueError as error:
                                    self.log_error_with_traceback(
                                        f"process_pics_table_data in {self.__class__.__name__}: invalid return_pic_data format",
                                        error
                                    )
                                    return False
                            else:
                                logging.debug(f"Unable to get data in {cluster}-{obj_pics_xml_data.variable}")
                        else:
                            logging.debug(f"Unable to get data in {cluster}-obj_pics_xml_data is None")

            return obj_xml_pic
        except Exception as error:
            self.log_error_with_traceback(
                f"Error in process_pics_table_data of {self.__class__.__name__}", error
            )
            return None

    def process_pixit_table_data(self, pixit_dict, obj_xml_pic, cluster):
        try:
            for heading in pixit_dict:
                for pics_xml in pixit_dict[heading]:
                    if pics_xml.variable is not None:
                        for _id in range(len(pics_xml.variable)):
                            obj_pixit_details = self.read_pics_data(pics_xml, _id)
                            if obj_pixit_details is not None:
                                obj_pixit_details.pics = obj_pixit_details.variable
                                obj_xml_pic.pixit[obj_pixit_details.variable] = obj_pixit_details
                                if obj_pixit_details.pics not in self.cluster_pixit_list:
                                    self.cluster_pixit_list.append(obj_pixit_details.pics)
                            else:
                                logging.debug(f"Unable to get PIXIT data in {cluster}-obj_pixit_details is None")

            return obj_xml_pic
        except Exception as error:
            self.log_error_with_traceback(
                f"Error in process_pixit_table_data ({cluster}) of {self.__class__.__name__}", error
            )
            return None

    def read_pics_data(self, pics_xml, _id):
        try:
            # Assigning the variable from pics_xml to the Name attribute in PicsXmlData
            obj_pics_xml = PicsXmlData(
                pics_xml.variable[_id],
                pics_xml.description[_id],
                pics_xml.mandatory_optional[_id],
                pics_xml.notes_additional[_id],
                pics_xml.reference_heading
            )
            # obj_pics_xml.variable = re.split(r'\(.*\)', obj_pics_xml.name)[0]
            return obj_pics_xml
        except Exception as error:
            self.log_error_with_traceback(
                f"Error in creating create_pics_xml of {self.__class__.__name__}", error
            )
            return None

    # region -Process upload PICS
    def process_upload_pics_object(self, obj_xml_pic: XmlData, obj_pics_xml_data: PicsXmlData, cluster: str,
                                   parent_heading: str, child_heading: str) -> None | tuple[
        XmlData, PicsXmlData, PicsDetails]:
        try:
            variable = obj_pics_xml_data.variable

            if variable == 'SWTCH.C.M.SwitchStatePolling':
                pass

            obj_pics_details = PicsDetails(variable, cluster)
            server_client_type = 'S'  # Initialize with default value

            if cluster == "Service Area Cluster Test Plan":
                pass

            if re.search(self.regex_mcore, variable):
                self.is_mcore_pics = True
                if variable not in obj_xml_pic.mcore:
                    obj_xml_pic.mcore[variable] = obj_pics_xml_data
                obj_pics_details.pics_type = AllTypePics.MCORE
                obj_pics_details.client_server = AllClusterSide.MCORE
                obj_pics_xml_data.pics = variable

                if cluster not in self.mcore_cluster_list:
                    self.mcore_cluster_list.append(cluster)
                if variable not in self.mcore_pics_list:
                    self.mcore_pics_list.append(variable)
                return obj_xml_pic, obj_pics_xml_data, obj_pics_details

            if match_regex_role := re.search(self.regex_role, variable):
                self._handle_role_pics(match_regex_role, obj_xml_pic, obj_pics_xml_data, obj_pics_details, variable,
                                       cluster, parent_heading)
                return obj_xml_pic, obj_pics_xml_data, obj_pics_details

            error_msg = f"Wrong PICS definition Table : {cluster}-{variable}-defined in {parent_heading}"
            is_not_child_heading = False

            for pattern, pics_type in self.regex_patterns:
                if match := re.search(pattern, variable):
                    is_not_child_heading, server_client,pics_type = self._process_pattern_match(match, obj_xml_pic,
                                                                                      obj_pics_xml_data,
                                                                                      obj_pics_details, pics_type,
                                                                                      variable, server_client_type,
                                                                                      cluster, pattern, parent_heading,
                                                                                      is_not_child_heading)
                    self._check_child_heading(is_not_child_heading, child_heading, pics_type, parent_heading, error_msg,
                                              server_client)
                    return obj_xml_pic, obj_pics_xml_data, obj_pics_details

            obj_pics_details.pics_type = AllTypePics.MANUALLY
            self._process_manually_pics(obj_xml_pic, obj_pics_xml_data, obj_pics_details, variable, parent_heading,
                                        cluster)
            return obj_xml_pic, obj_pics_xml_data, obj_pics_details

        except Exception as e:
            self.log_error_with_traceback(f"Error processing PICS object: {obj_pics_xml_data} in cluster: {cluster}", e)
            if obj_pics_xml_data is not None:
                logging.error(
                    f"XmlPicsExploration - process_upload_pics_object - Error in {cluster} {obj_pics_xml_data.variable}")
            else:
                logging.error(
                    f"XmlPicsExploration - process_upload_pics_object - Error in {cluster} obj_pics_detail is None")
            return None

    def _handle_role_pics(self, match_regex_role, obj_xml_pic, obj_pics_xml_data, obj_pics_details, variable, cluster,
                          parent_heading):
        try:
            obj_pics_xml_data.pics = match_regex_role.group(0)
            obj_pics_xml_data.name = match_regex_role.group(1)
            if obj_xml_pic is not None:
                if variable not in obj_xml_pic.role:
                    obj_xml_pic.role[variable] = obj_pics_xml_data
                obj_pics_details.pics_type = AllTypePics.ROLE
                obj_pics_details.client_server = AllClusterSide.ROLE
            if AllClusterSide.ROLE.value.lower() != parent_heading.lower():
                logging.debug(f" Wrong Role PICS Table- {cluster}-{variable} -defined in {parent_heading}")
        except Exception as e:
            self.log_error_with_traceback(
                f"Error processing role PICS object: {obj_pics_xml_data} in cluster: {cluster}", e)

    def _process_pattern_match(self, match, obj_xml_pic, obj_pics_xml_data, obj_pics_details, pics_type, variable,
                               server_client_type, cluster, pattern, parent_heading, is_not_child_heading):
        try:
            obj_pics_details.client_server = AllClusterSide.SERVER
            self.is_other_pics = True

            if len(match.regs) > 6:
                obj_pics_xml_data.pics = match.group(1)
                obj_pics_xml_data.id = f'0x{match.group(5):02}'
                obj_pics_xml_data.name = match.group(6)
                server_client_type = match.group(3)

            server_client_type, is_not_child_heading,pics_type = self._update_obj_pics_xml_data_by_pattern(match,
                                                                                                 obj_pics_xml_data,
                                                                                                 pattern,
                                                                                                 parent_heading,
                                                                                                 server_client_type,
                                                                                                 is_not_child_heading,pics_type)

            server_client = ServerClient.SERVER
            if server_client_type == 'C':
                server_client = ServerClient.CLIENT
                obj_pics_details.client_server = AllClusterSide.CLIENT

            obj_pics_details.pics_type = pics_type
            if obj_xml_pic is not None:
                server_client_data = obj_xml_pic.serverclient[server_client].data[pics_type]
                if variable not in server_client_data:
                    server_client_data[variable] = obj_pics_xml_data
                    self._map_feature_name_pics(obj_xml_pic, server_client, obj_pics_xml_data, variable, pattern)
            return is_not_child_heading, server_client,pics_type
        except Exception as e:
            self.log_error_with_traceback(
                f"Error processing pattern match for PICS object: {obj_pics_xml_data} in cluster: {cluster}", e)

    def _update_obj_pics_xml_data_by_pattern(self, match, obj_pics_xml_data, pattern, parent_heading,
                                             server_client_type, is_not_child_heading,pics_type):
        try:
            if pattern == self.regex_attributes:
                obj_pics_xml_data.id = f'0x{match.group(5):04}'
            elif pattern == self.regex_attributes_extra_dot:
                obj_pics_xml_data.id = f'0x{match.group(5):04}'
                obj_pics_xml_data.name = match.group(7)
                obj_pics_xml_data.pics = match.group(1) + "." + match.group(7)
            elif pattern == self.regex_attributes_spl:
                obj_pics_xml_data.id = f'0x{match.group(5):04}'
            elif pattern == self.regex_attributes_write:
                obj_pics_xml_data.id = f'0x{match.group(5):04}'
                obj_pics_xml_data.commands_type = match.group(7)
                obj_pics_xml_data.pics = match.group(1) + "." + match.group(7)
            elif pattern == self.regex_commands:
                obj_pics_xml_data.name = match.group(7)
                obj_pics_xml_data.commands_type = match.group(6)
                if obj_pics_xml_data.commands_type == "Tx":
                    pics_type = AllTypePics.COMMANDS_GENERATED
            elif pattern == self.regex_events:
                obj_pics_xml_data.id = f'0x{match.group(5):02}'
            elif pattern == self.regex_features:
                obj_pics_xml_data.id = f'0x{match.group(5):02}'
            elif pattern == self.regex_sc_manual:
                obj_pics_xml_data.pics = match.group(0)
                obj_pics_xml_data.name = match.group(4)
                server_client_type = match.group(2)
            elif pattern == self.regex_manual:
                is_not_child_heading = True
                obj_pics_xml_data.pics = match.group(0)
                obj_pics_xml_data.name = match.group(3)
                if parent_heading == 'Client':
                    server_client_type = 'C'
            return server_client_type, is_not_child_heading,pics_type
        except Exception as e:
            self.log_error_with_traceback(f"Error updating PICS XML data by pattern: {pattern}", e)

    def handle_mapping(self, obj_xml_pic, server_client, obj_pics_xml_data, variable, conformance_type):
        try:
            obj_xml_pic.feature_code[server_client][obj_pics_xml_data.name] = obj_pics_xml_data.pics

            regex_o_a = r"O.a"
            if re.search(regex_o_a, str(obj_pics_xml_data.mandatory_optional)):
                obj_xml_pic.o_a_pics_head_dict[server_client][conformance_type].append(variable.split("(")[0])

            regex_o = r"(O\.(a|b|c)\+?)"
            match = re.search(regex_o, obj_pics_xml_data.mandatory_optional)
            dict_key = match.group(1) if match else ''
            if dict_key:
                if dict_key not in obj_xml_pic.o_conformance_dict:
                    obj_xml_pic.o_conformance_dict[dict_key] = copy.deepcopy(obj_xml_pic.nested_dict)
                obj_xml_pic.o_conformance_dict[dict_key][server_client][conformance_type].append(variable.split("(")[0])
        except Exception as e:
            self.log_error_with_traceback(
                f"Error mapping feature name for PICS object: {obj_pics_xml_data} in variable: {variable}", e)

    def _map_feature_name_pics(self, obj_xml_pic, server_client, obj_pics_xml_data, variable, pattern):
        try:
            if pattern == self.regex_features:
                self.handle_mapping(obj_xml_pic, server_client, obj_pics_xml_data, variable, AllTypePics.FEATURES)
            elif pattern == self.regex_sc_manual:
                self.handle_mapping(obj_xml_pic, server_client, obj_pics_xml_data, variable, AllTypePics.MANUALLY)
        except Exception as e:
            self.log_error_with_traceback(
                f"Error mapping feature name for PICS object: {obj_pics_xml_data} in variable: {variable}", e)

    def _check_child_heading(self, is_not_child_heading, child_heading, pics_type, parent_heading, error_msg,
                             server_client):
        try:
            if child_heading is not None:
                if is_not_child_heading:
                    if child_heading.lower() != pics_type.value[0].lower():
                        logging.debug(error_msg + f"-{child_heading}")
                elif (child_heading.lower() != pics_type.value[0].lower()
                      or server_client.value.lower() != parent_heading.lower()):
                    if child_heading.lower() not in ["write attributes", "specific attribute features"]:
                        logging.debug(error_msg + f"-{child_heading}")
            else:
                logging.debug(error_msg + f"-No child heading")
        except Exception as e:
            self.log_error_with_traceback(f"Error checking child heading with parent heading: {parent_heading}", e)

    def _process_manually_pics(self, obj_xml_pic, obj_pics_xml_data, obj_pics_details, variable, parent_heading,
                               cluster):
        try:
            # Determine the server client based on parent_heading
            server_client = ServerClient.SERVER
            if parent_heading.lower() == 'client':
                server_client = ServerClient.CLIENT
                obj_pics_details.client_server = AllClusterSide.CLIENT

            # Process obj_xml_pic if it is not None
            if obj_xml_pic is not None:
                obj_pics_xml_data.pics = obj_pics_xml_data.variable
                server_client_data = obj_xml_pic.serverclient[server_client].data[AllTypePics.MANUALLY]
                if variable not in server_client_data:
                    server_client_data[variable] = obj_pics_xml_data

                # Log the addition of the variable into server_client.manually
                logging.debug(f"{self.debug_text} {cluster}-{variable} - Added into {server_client}.manually")

            # Additional check for obj_pics_details.pics_type
            obj_pics_details.pics_type = AllTypePics.MANUALLY
            if parent_heading.lower() != "pixit":
                logging.debug(f"Wrong PICS definition Table : {cluster}-{variable}-defined in {parent_heading}")

        except Exception as e:

            # Error handling with detailed logging
            self.log_error_with_traceback(
                f"XmlPicsExploration - process_upload_pics_object: {str(e)} in cluster: {cluster}", e)


    # endregion -Process upload PICS

    def update_missing_top_level_cluster_pics_data(self, reference_tl_pics):
        try:
            for cluster_name, obj_xml_pic in self.xml_data.items():
                if cluster_name == "Access Control Enforcement Test Plan":
                    a = 1
                for pics in obj_xml_pic.missing_top_pics:
                    if pics in self.test_plan_cluster_pics_dict:
                        pics_cluster_name = ""
                        if len(self.test_plan_cluster_pics_dict[pics]) == 1:
                            pics_cluster_name = self.test_plan_cluster_pics_dict[pics][0]
                        elif len(self.test_plan_cluster_pics_dict[pics]) > 1:
                            for s_no, cluster in enumerate(self.test_plan_cluster_pics_dict[pics], start=1):
                                cluster_pics_code = pics.split('.')[0]
                                duplicate_pics_code = self.xml_data[cluster].pics_code
                                if cluster_pics_code in duplicate_pics_code:
                                    pics_cluster_name = cluster

                        obj_xml_pic.other_cluster_pics[pics] = ClusterReference(
                            pics_cluster_name, reference_tl_pics[pics]
                        )
                    else:
                        match = re.search(r"[A-Z]+\.([CS])\.", pics)
                        server_client_type = match.group(1) if match else 'S'
                        server_client = ServerClient.CLIENT if server_client_type == 'C' else ServerClient.SERVER
                        server_client_data = obj_xml_pic.serverclient[server_client].data[AllTypePics.MANUALLY]
                        reference_heading = reference_tl_pics.get(pics, "")
                        description = self.get_description(pics)

                        obj_pics_xml_data = PicsXmlData(pics, description, 'O', "", reference_heading)
                        obj_pics_xml_data.pics = pics
                        if pics not in server_client_data:
                            server_client_data[pics] = obj_pics_xml_data

            return True
        except Exception as error:
            self.log_error_with_traceback(
                f"Error in update_missing_top_level_cluster_pics_data of {self.__class__.__name__}", error
            )
            return None

    def update_missing_top_level_pics_data(self, missing_top_pics, obj_xml_pic, reference_tl_pics):
        try:
            for pics in missing_top_pics:
                match = re.search(r"[A-Z]+\.([CS])\.", pics)
                server_client_type = match.group(1) if match else 'S'
                server_client = ServerClient.CLIENT if server_client_type == 'C' else ServerClient.SERVER
                server_client_data = obj_xml_pic.serverclient[server_client].data[AllTypePics.MANUALLY]
                reference_heading = reference_tl_pics.get(pics, "")
                description = self.get_description(pics)

                obj_pics_xml_data = PicsXmlData(pics, description, 'O', "", reference_heading)
                obj_pics_xml_data.pics = pics

                if pics not in server_client_data:
                    server_client_data[pics] = obj_pics_xml_data

            return obj_xml_pic
        except Exception as error:
            self.log_error_with_traceback(
                f"Error in update_missing_top_level_pics_data of {self.__class__.__name__}", error
            )
            return None

    def get_description(self, item):
        try:
            description_map = {
                r"\.C\.AO-READ$": "Read all supported optional attributes",
                r"\.C\.AM-READ$": "Read all supported mandatory attributes",
                r"\.C\.AM-WRITE$": "Write all supported mandatory attributes",
                r"\.C\.AO-WRITE$": "Write all supported optional attributes",
                r"\.S\.C$": "Verifies the command functionality of the server",
                r"\.S\.A$": "Verifies the behavior of the non-global attributes of the server",
                r"\.S\.E$": "Verifies the event reporting functionality of the server",
                r"\.C\.C$": "Verifies the command functionality of the client",
                r"\.C\.A$": "Verifies the behavior of the non-global attributes of the client",
                r"\.C\.E$": "Verifies the event reporting functionality of the client",
                r"\.S\.Am$": "List of non-global attributes that are specified as being mandatory",
                r"\.S\.Ao$": "List of non-global attributes that are specified as being optional",
            }

            # Check each pattern and return the corresponding description
            for pattern, description in description_map.items():
                if re.search(pattern, item):
                    return description

            return ""  # Default case if no patterns match

        except Exception as error:
            self.log_error_with_traceback(
                f"Error in get_description of {self.__class__.__name__}", error
            )
            return None

