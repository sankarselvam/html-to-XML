import logging
import re
from collections import OrderedDict
import xlsxwriter

import numpy as np
import pandas as pd

from tp_data_classes import ServerClient, PicsPixitType, AllTypePics, ClusterReference


class StatusFinder:
    """
        Class to handle status and conformance data related to PICS and PIXIT.
    """

    REPLACEMENTS_LOGIC = {
        "!": " NOT ",
        "&": " AND ",
        "|": " OR "
    }

    CONFORMANCE_COUNT_TEMPLATE = {
        'O': 0,
        'M': 0,
        'X': 0,
        'M Provisional': 0,
        'NOT Zigbee': 0,
        'Feature': 0,
        'O.a+': 0,
        'Double line': 0,
        'Duplicate': 0,
        'Others': 0,
        'PICS': 0,
        'TOTAL': 0,
        'MCORE': 0
    }

    def __init__(self):
        # Initialize conformance count templates for PICS and PIXIT
        self.pics_pixit_count = {
            PicsPixitType.PICS: self.CONFORMANCE_COUNT_TEMPLATE.copy(),
            PicsPixitType.PIXIT: self.CONFORMANCE_COUNT_TEMPLATE.copy()
        }

        # Boolean flag for PICS reference Excel
        self.pics_ref_excel = True

        # Dictionaries for storing conformance and duplicate data
        self.pics_conformance_data = OrderedDict()
        self.duplicate_pics_data = OrderedDict()
        self.pixit_conformance_data = OrderedDict()
        self.mcore_conformance_data = OrderedDict()
        self.duplicate_pixit_data = OrderedDict()

    def process_cluster_data(self, data_dict):
        try:
            logging.info(f"Executing process_cluster_data in {self.__class__.__name__}")


            for cluster_name, xml_data in data_dict.items():
                # Access the attributes and perform operations for each cluster
                feature_dict = {}
                # Accessing the serverclient attribute (OrderedDict)
                for server_client, data in xml_data.serverclient.items():
                    pics_pixit_type = PicsPixitType.PICS
                    # Get the ServerClientDataType values
                    server_client_values = list(data.data.keys())

                    # Accessing the data attribute within ServerClientData
                    for pic_type in server_client_values:
                        pic_type_name = pic_type.value

                        # Accessing the individual data within the pic_type
                        pic_data = data.data.get(pic_type)
                        if pic_data and len(pic_data) > 0:
                            for pics, obj_pics_xml_data in pic_data.items():
                                if pics not in self.pics_conformance_data:
                                    self.pics_conformance_data[pics] = []
                                    self.duplicate_pics_data[pics] = [cluster_name]
                                else:
                                    self.pics_pixit_count[pics_pixit_type]['Duplicate'] += 1
                                    self.duplicate_pics_data[pics].append(cluster_name)

                                self.pics_pixit_count[pics_pixit_type]['PICS'] += 1
                                self.pics_conformance_data[pics].append(obj_pics_xml_data.mandatory_optional)

                                feature_dict = xml_data.feature_code[server_client]
                                regex_o = r"(O\.(a|b|c)\+?)"
                                match = re.search(regex_o, obj_pics_xml_data.mandatory_optional)
                                dict_key =match.group(1) if match else ''
                                # Retrieve the nested dictionary and safely access the desired keys
                                o_conformance_dict = xml_data.o_conformance_dict.get(dict_key, {})
                                server_client_dict = o_conformance_dict.get(server_client, {})
                                o_a_pics_list = server_client_dict.get(pic_type, [])

                                #o_a_pics_list = xml_data.o_a_pics_head_dict[server_client][pic_type]

                                is_mcore = False
                                role = xml_data.role
                                return_text = self.find_status(pics, pics_pixit_type,
                                                               obj_pics_xml_data.mandatory_optional, feature_dict,
                                                               is_mcore,
                                                               server_client, role,
                                                               o_a_pics_list)
                                if isinstance(return_text, bool):
                                    logging.debug(f"Unable to get Conformance values of in {pics}-process_cluster_data")
                                else:
                                    conformance_value, conformance_text = return_text
                                    obj_pics_xml_data.status_conformance = conformance_value
                                    obj_pics_xml_data.status_text = conformance_text
                                    self.pics_conformance_data[pics].extend(conformance_text)
                                    self.pics_conformance_data[pics].extend(conformance_value)
                        else:
                            print(f"No data found for Pic Type: {pic_type_name}")

                for pics, obj_pics_xml_data in xml_data.mcore.items():
                    is_mcore = True
                    pics_pixit_type = PicsPixitType.PICS

                    if pics not in self.mcore_conformance_data:
                        self.mcore_conformance_data[pics] = []
                        self.duplicate_pics_data[pics] = [cluster_name]
                    else:
                        self.pics_pixit_count[pics_pixit_type]['Duplicate'] += 1
                        self.duplicate_pics_data[pics].append(cluster_name)

                    self.pics_pixit_count[pics_pixit_type]['PICS'] += 1
                    self.mcore_conformance_data[pics].append(obj_pics_xml_data.mandatory_optional)

                    return_text = self.find_status(pics, pics_pixit_type, obj_pics_xml_data.mandatory_optional,
                                                   feature_dict, is_mcore)
                    if isinstance(return_text, bool):
                        logging.debug(f"Unable to get Conformance values of in {pics}-process_cluster_data")
                    else:
                        conformance_value, conformance_text = return_text
                        obj_pics_xml_data.status_conformance = conformance_value
                        obj_pics_xml_data.status_text = conformance_text
                        self.mcore_conformance_data[pics].extend(conformance_text)
                        self.mcore_conformance_data[pics].extend(conformance_value)

                for pixit in xml_data.pixit:
                    is_mcore = False
                    pics_pixit_type = PicsPixitType.PIXIT
                    role = xml_data.role
                    # logging.debug(f"PIXIT --- PIXIT---- {pixit}")
                    obj_pixit_xml_data = xml_data.pixit[pixit]
                    if pixit not in self.pixit_conformance_data:
                        self.pixit_conformance_data[pixit] = []
                        self.duplicate_pixit_data[pixit] = [cluster_name]
                    else:
                        self.pics_pixit_count[pics_pixit_type]['Duplicate'] += 1
                        self.duplicate_pixit_data[pixit].append(cluster_name)

                    self.pics_pixit_count[pics_pixit_type]['PICS'] += 1
                    self.pixit_conformance_data[pixit].append(obj_pixit_xml_data.mandatory_optional)

                    condition_text = next(iter(data_dict[cluster_name].role))
                    return_text = self.find_status(pixit, pics_pixit_type, obj_pixit_xml_data.mandatory_optional,
                                                   feature_dict, is_mcore, condition_text, role)
                    if isinstance(return_text, bool):
                        logging.debug(f"Unable to get Conformance values of in {pixit}-process_cluster_data")
                    else:
                        conformance_value, conformance_text = return_text
                        obj_pixit_xml_data.status_conformance = conformance_value
                        obj_pixit_xml_data.status_text = conformance_text
                        self.pixit_conformance_data[pixit].extend(conformance_text)
                        self.pixit_conformance_data[pixit].extend(conformance_value)

            self.pics_ref_excel = True
            self.duplicate_pics_details_remove(PicsPixitType.PICS, data_dict)
            self.duplicate_pics_details_remove(PicsPixitType.PIXIT, data_dict)
            self.generate_pics_pixit_report(PicsPixitType.PICS)
            self.generate_pics_pixit_report(PicsPixitType.PIXIT)

            return data_dict
        except Exception as error:
            logging.error(f"Error in process_cluster_data of {StatusFinder.__name__}: {str(error)}")
            return None

    def generate_pics_pixit_report(self, pics_pixit_type):
        try:
            pics_pixit_name = "PICS"
            duplicate_data = self.duplicate_pics_data
            if pics_pixit_type == PicsPixitType.PIXIT:
                pics_pixit_name = "PIXIT"
                duplicate_data = self.duplicate_pixit_data

            for key, value in self.pics_pixit_count[pics_pixit_type].items():
                if key == 'PICS':
                    key = pics_pixit_name

                log_message = f"{pics_pixit_type.value} - {key} count: {value}"
                logging.info(log_message)

            missing_count = self.pics_pixit_count[pics_pixit_type]['Double line'] + \
                            self.pics_pixit_count[pics_pixit_type]['TOTAL'] - \
                            self.pics_pixit_count[pics_pixit_type]['O'] - \
                            self.pics_pixit_count[pics_pixit_type]['M'] - \
                            self.pics_pixit_count[pics_pixit_type]['M Provisional'] - \
                            self.pics_pixit_count[pics_pixit_type]['X'] - \
                            self.pics_pixit_count[pics_pixit_type]['NOT Zigbee'] - \
                            self.pics_pixit_count[pics_pixit_type]['Feature'] - \
                            self.pics_pixit_count[pics_pixit_type]['O.a+'] - \
                            self.pics_pixit_count[pics_pixit_type]['MCORE']
            all_difference = self.pics_pixit_count[pics_pixit_type]['PICS'] - \
                             self.pics_pixit_count[pics_pixit_type]['TOTAL']

            missing_count_message = f"Difference between {pics_pixit_name} count vs TOTAL count: {all_difference}"
            all_difference_message = f"All_difference: {missing_count}"

            logging.info(f"{pics_pixit_type.value} - {missing_count_message}")
            logging.info(f"{pics_pixit_type.value} - {all_difference_message}")

            file_name = "Conformance_values_all_PICS.xlsx"
            conformance_data = self.pics_conformance_data
            column_heading_name = "PICS ID"
            if pics_pixit_type == PicsPixitType.PIXIT:
                file_name = "Conformance_values_all_PIXIT.xlsx"
                conformance_data = self.pixit_conformance_data
                column_heading_name = "PIXIT ID"

            if self.pics_ref_excel:
                # Determine the maximum number of elements in any list
                max_elements = max(len(list(lst)) for lst in conformance_data.values())

                # Generate column names based on the maximum number of elements
                column_names = ['S.No', column_heading_name] + [f'Value{i + 1}' for i in range(max_elements)]

                # Create a list of lists for the data rows
                data_rows = []

                # Iterate over the original data and append rows to the list
                for idx, (key, value) in enumerate(conformance_data.items(), start=1):
                    row = [idx, key] + value + [''] * (max_elements - len(value))
                    data_rows.append(row)

                # Create a DataFrame from the data rows and column names
                df = pd.DataFrame(data_rows, columns=column_names)

                # Create an Excel writer using pandas
                writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

                # Write the DataFrame to the Excel file
                df.to_excel(writer, sheet_name='Sheet1', index=False)

                # Save the Excel file
                writer.close()

            # Write duplicate data details to another Excel file
            duplicate_file_name = f"Duplicate_{pics_pixit_name}_Details.xlsx"
            duplicate_rows = []

            s_no=1
            for index, (pics, cluster_names) in enumerate(duplicate_data.items(), start=1):
                if len(cluster_names) > 1:
                    for i, cluster_name in enumerate(cluster_names, start=1):
                        duplicate_rows.append([s_no, pics, f'{i}. {cluster_name}'])
                    s_no+=1

            duplicate_df = pd.DataFrame(duplicate_rows, columns=['S.No', f'{pics_pixit_name}', 'Cluster Details'])

            # Create an Excel writer for the duplicate data
            duplicate_writer = pd.ExcelWriter(duplicate_file_name, engine='xlsxwriter')

            # Write the DataFrame to the Excel file
            duplicate_df.to_excel(duplicate_writer, sheet_name='Sheet1', index=False)

            # Save the Excel file
            duplicate_writer.close()


        except Exception as error:
            logging.exception(f"Error in generate_pics_pixit_report of {StatusFinder.__name__}: {str(error)}")
            return False

    '''
    def duplicate_pics_details_remove(self, pics_pixit_type, data_dict):
        try:
            pics_pixit_name = "PICS"
            parent_pics_dict = OrderedDict()
            duplicate_pics_dict = OrderedDict()
            duplicate_data = self.duplicate_pics_data

            if pics_pixit_type == PicsPixitType.PIXIT:
                pics_pixit_name = "PIXIT"
                duplicate_data = self.duplicate_pixit_data

            # Create an Excel file and a worksheet
            repeated_file_name = f"Repeated_{pics_pixit_name}_Details.xlsx"
            workbook = xlsxwriter.Workbook(repeated_file_name)
            worksheet = workbook.add_worksheet()

            # Write headers to the Excel file
            worksheet.write('A1', 'Index')
            pics_pixit_column_name=f"Multiple {pics_pixit_name}"
            worksheet.write('B1', pics_pixit_column_name)
            worksheet.write('C1', 'Parent definition')
            worksheet.write('D1', 'Duplicate definition')

            row = 1
            index = 0

            for pics, cluster_names in duplicate_data.items():
                if len(cluster_names) > 1:
                    cluster_pics_code = pics.split('.')[0]

                    if not cluster_pics_code.startswith("MCORE"):



                        for s_no, cluster_name in enumerate(cluster_names, start=1):
                            duplicate_pics_code = data_dict[cluster_name].pics_code

                            if cluster_pics_code in duplicate_pics_code:
                                index += 1
                                worksheet.write(row, 0, index)
                                worksheet.write(row, 1, pics)
                                worksheet.write(row, 2, cluster_name)
                                parent_pics_dict[pics] = cluster_name
                            else:
                                obj_xml_data = data_dict[cluster_name]

                                for server_client, data in obj_xml_data.serverclient.items():
                                    server_client_values = list(data.data.keys())

                                    for pic_type in server_client_values:
                                        pic_data = data.data.get(pic_type)

                                        if pics in pic_data:
                                            data_dict[cluster_name].removed_pics[pics] = pic_data[pics]
                                            del pic_data[pics]

                                            # Write to Excel

                                            worksheet.write(row, 3, cluster_name)

                                            if cluster_name not in duplicate_pics_dict:
                                                duplicate_pics_dict[cluster_name] = []
                                            duplicate_pics_dict[cluster_name].append(pics)

                                #worksheet.write(row, 3, f"  {s_no}. Duplicate definition: {cluster_name}")
                                row += 1


            for cluster_name, pics_list in duplicate_pics_dict.items():
                for duplicate_pics in pics_list:
                    parent_cluster = parent_pics_dict[duplicate_pics]
                    data_dict[cluster_name].other_cluster_pics[duplicate_pics] = ClusterReference(
                        parent_cluster,
                        data_dict[cluster_name].removed_pics[duplicate_pics].reference
                    )

            # Close the Excel file
            workbook.close()

            return True

        except Exception as error:
            logging.exception(f"Error in duplicate_pics_details_remove of {StatusFinder.__name__}: {str(error)}")
            return False
    '''
    def duplicate_pics_details_remove(self, pics_pixit_type, data_dict):
        try:
            pics_pixit_name = "PICS"
            parent_pics_dict = OrderedDict()
            duplicate_pics_dict = OrderedDict()
            duplicate_data = self.duplicate_pics_data
            if pics_pixit_type == PicsPixitType.PIXIT:
                pics_pixit_name = "PIXIT"
                duplicate_data = self.duplicate_pixit_data
            index = 1
            for pics, cluster_names in duplicate_data.items():
                if len(cluster_names) > 1:

                    cluster_pics_code = pics.split('.')[0]
                    if not cluster_pics_code.startswith("MCORE"):
                        logging.debug(
                            f"{index}. Multiple {pics_pixit_name} definitions found in - {pics},Cluster details:")
                        for s_no, cluster_name in enumerate(cluster_names, start=1):
                            duplicate_pics_code = data_dict[cluster_name].pics_code
                            if cluster_pics_code in duplicate_pics_code:
                                logging.debug(f"  {s_no}. Parent definition : {cluster_name} ")
                                parent_pics_dict[pics] = cluster_name
                            else:
                                obj_xml_data = data_dict[cluster_name]

                                for server_client, data in obj_xml_data.serverclient.items():
                                    server_client_values = list(data.data.keys())
                                    for pic_type in server_client_values:
                                        pic_type_name_0 = pic_type.value[0]
                                        pic_data = data.data.get(pic_type)
                                        if pics in pic_data:
                                            data_dict[cluster_name].removed_pics[pics] = pic_data[pics]
                                            del pic_data[pics]
                                            
                                            if cluster_name not in duplicate_pics_dict:
                                                duplicate_pics_dict[cluster_name] = []
                                            duplicate_pics_dict[cluster_name].append(pics)

                                logging.debug(f"  {s_no}. Duplicate definition: {cluster_name} ")
                        index += 1

            for cluster_name in duplicate_pics_dict:
                pics_list = duplicate_pics_dict[cluster_name]
                for duplicate_pics in pics_list:
                    parent_cluster = parent_pics_dict[duplicate_pics]
                    data_dict[cluster_name].other_cluster_pics[duplicate_pics] = ClusterReference(parent_cluster,
                                                                                                  data_dict[
                                                                                                      cluster_name].removed_pics[
                                                                                                      duplicate_pics].reference)
            a = 1
        except Exception as error:
            logging.exception(f"Error in duplicate_pics_details_remove of {StatusFinder.__name__}: {str(error)}")
            return False

    def find_status(self, pics, pics_pixit_type, conformance, feature_dict, is_mcore, server_client=ServerClient.SERVER,
                    role=None,
                    o_a_pics_list=None):
        if role is None:
            role = {}
        if o_a_pics_list is None:
            o_a_pics_list = []

        try:

            if pics == "ICDM.S.A0003(RegisteredClients)":
                a = 1
            if pics == "OO.S.F02(OFFONLY)":
                a=1
            st_conformance = []
            st_text = []
            if conformance == np.int64(0):
                conformance = 'O'
            conformance_list = conformance.split(",")
            if len(conformance_list) > 1:
                temp_list_1 = []
                temp_list_2 = []
                for item in conformance_list:
                    if item.strip().startswith("["):
                        temp_list_1.append(item.strip())
                    else:
                        temp_list_2.append(item.strip())
                temp_list_1.extend(temp_list_2)
                conformance_list = temp_list_1
            is_first = True
            for conformance_text in conformance_list:
                if not is_first:
                    a = 1
                return_text = self.find_conformance(pics, pics_pixit_type, conformance_text, feature_dict, is_first,
                                                    is_mcore, server_client, role, o_a_pics_list)
                is_first = False
                if isinstance(return_text, bool):
                    logging.debug(f"Unable to get Conformance values of in {pics} - find_status")
                elif return_text is None:
                    self.pics_pixit_count[pics_pixit_type]['Others'] += 1
                else:
                    conformance_value, conformance_text = return_text
                    st_conformance.extend(conformance_value)
                    st_text.extend(conformance_text)
            return st_conformance, st_text

        except Exception as error:
            logging.exception(f"Error in find_status of {StatusFinder.__name__}: {str(error)}")
            return False

    def find_conformance(self, pics, pics_pixit_type, conformance_text, feature_dict, is_first, is_mcore, server_client,
                         role,
                         o_a_pics_list):
        try:

            if pics == "ICDM.S.F02(LITS)":
                a = 1
            if conformance_text=='OO.S: [!(LT|DF)]':
                a=1
            if is_first:
                if not is_mcore:
                    self.pics_pixit_count[pics_pixit_type]['TOTAL'] += 1
                else:
                    self.pics_pixit_count[pics_pixit_type]['MCORE'] += 1
            else:
                self.pics_pixit_count[pics_pixit_type]['Double line'] += 1
            if pics == "PCC.S.A0003(MinConstPressure)":
                a = 1
            condition_text = ""
            match_sc = re.findall(r"^[A-Z a-z]+\.[SC]", pics)
            match_m = re.findall(r"^([A-Z a-z]+)\.M", pics)
            if match_sc:
                condition_text = match_sc[0]
            elif match_m:
                condition_text = match_m[0] + ".S"
                if server_client == ServerClient.CLIENT:
                    condition_text = match_m[0] + ".C"
            else:
                condition_text = pics.split(".")[0] + ".S"
            if pics_pixit_type == PicsPixitType.PIXIT:
                # PicsPixitType.PIXIT -server_client contains conformance text
                condition_text = server_client
            if is_mcore or condition_text not in role.keys():
                condition_text = ""

            st_conformance = []
            st_text = []
            if ':' in conformance_text:
                split_item = conformance_text.strip().split(':')
                split_item[1] = re.sub(r'optional', "O", split_item[1].strip(), flags=re.IGNORECASE)
                split_item[1] = re.sub(r'mandatory', "M", split_item[1].strip(), flags=re.IGNORECASE)
                if split_item[1] == 'O' or split_item[1] == 'M':
                    st_conformance.append(split_item[1])
                    st_text_temp=split_item[0].split("(")[0].strip()
                    # st_text_result = feature_dict[st_text_temp] if st_text_temp in feature_dict else st_text_temp
                    st_text_result = feature_dict.get(st_text_temp.replace('[', '').replace(']', ''), st_text_temp)

                    st_text.append(st_text_result)
                    if split_item[1] == 'O':
                        self.pics_pixit_count[pics_pixit_type]['O'] += 1
                    if split_item[1] == 'M':
                        self.pics_pixit_count[pics_pixit_type]['M'] += 1
                    return st_conformance, st_text
                elif 'O.a' in split_item[1] or 'O.a+' in split_item[1] or 'O.b' in split_item[1] or 'O.b+' in split_item[1]:
                    logging.debug(f"Spl type Conformance format in {pics} - {conformance_text}")
                    first_text = split_item[0].split("(")[0].strip() + " AND "
                    conformance_text = conformance_text.split(':')[1].strip()
                    st_conformance, st_text = self.process_o_a_plus(pics, pics_pixit_type, o_a_pics_list,
                                                                    conformance_text)
                    st_text[0] = first_text + st_text[0]
                    return st_conformance, st_text

                else:
                    # logging.debug(f" :  Conformance values of in {pics} - {conformance_text}")
                    conformance_text = conformance_text.split(':')[1].strip()

            if conformance_text in ('O', 'M', 'X', 'Optional', 'O *'):
                # if is_first:
                if conformance_text == 'O':
                    self.pics_pixit_count[pics_pixit_type]['O'] += 1
                elif conformance_text == 'O *':
                    self.pics_pixit_count[pics_pixit_type]['O'] += 1
                    conformance_text = 'O'
                elif conformance_text == 'Optional':
                    self.pics_pixit_count[pics_pixit_type]['O'] += 1
                    conformance_text = 'O'
                elif conformance_text == 'M':
                    self.pics_pixit_count[pics_pixit_type]['M'] += 1
                elif conformance_text == 'X':
                    self.pics_pixit_count[pics_pixit_type]['X'] += 1
                st_text.append(condition_text)
                st_conformance.append(conformance_text)
                return st_conformance, st_text
            elif conformance_text == 'M Provisional':
                self.pics_pixit_count[pics_pixit_type]['M Provisional'] += 1
                st_text.append(condition_text)
                st_conformance.append('M')
                return st_conformance, st_text

            elif conformance_text == "O.a+" or conformance_text == "O.a" or conformance_text == "O.b+" or conformance_text == "O.b":
                st_conformance, st_text = self.process_o_a_plus(pics, pics_pixit_type, o_a_pics_list, conformance_text)
                return st_conformance, st_text


            else:
                is_valid = False
                optional_str = 'M'
                regex_split_square = r"^\[(?P<Name>.*)\]$"
                if re.search(regex_split_square, conformance_text):
                    match_level1 = re.finditer(regex_split_square, conformance_text)
                    for match in match_level1:
                        _conformance = match.group("Name").strip()
                        optional_str = 'O'
                        conformance_text = _conformance
                        is_valid = True
                if condition_text == conformance_text:
                    is_valid = True
                    logging.debug(f"PICS values without Comformance {pics} - {conformance_text}")
                conformance_text_old=conformance_text

                text = "CMOCONC.S.F00(MEA)"
                #pattern = r"^[A-Z]+\.[CS]\.[FCE]\d{2}|A\d{4}\([A-Z]+\)$"
                pattern=r"^([A-Z]+|\[[A-Z]+)\.[CS]\.([FCE]\d{2}|A\d{4})\([A-Z]"

                if conformance_text=="DGETH.S.F00(PKTCNT)":
                    pass
                is_valid = True
                conformance_text = self.reformat_conformance_text(conformance_text)
                for key, value in feature_dict.items():
                    pattern = r'\b' + re.escape(key) + r'\b'
                    if pics_pixit_type == PicsPixitType.PIXIT:
                        value = re.sub(r'\.C\.', '.S.', value)
                    if re.search(pattern, conformance_text):
                        is_valid = True
                        conformance_text = re.sub(pattern, value, conformance_text)
                if is_valid:
                    self.pics_pixit_count[pics_pixit_type]['Feature'] += 1
                    st_conformance.append(optional_str)
                    st_text.append(conformance_text)
                    return st_conformance, st_text
                if conformance_text.startswith("MCORE"):
                    self.pics_pixit_count[pics_pixit_type]['MCORE'] += 1
                    st_conformance.append(optional_str)
                    st_text.append(conformance_text)
                    return st_conformance, st_text
                if conformance_text.startswith("NOT Zigbee"):
                    self.pics_pixit_count[pics_pixit_type]['NOT Zigbee'] += 1
                    st_conformance.append('M')
                    st_text.append(condition_text)
                    return st_conformance, st_text
                if pics_pixit_type == PicsPixitType.PIXIT:
                    regex_role = r"^([\w]+)\.([SC])$"
                    if re.search(regex_role, conformance_text):
                        if optional_str == 'M':
                            self.pics_pixit_count[pics_pixit_type]['M'] += 1
                        if optional_str == 'O':
                            self.pics_pixit_count[pics_pixit_type]['O'] += 1
                        st_conformance.append(optional_str)
                        st_text.append(conformance_text)
                        return st_conformance, st_text

                logging.debug(f"Unable to find Conformance values of in {pics} - {conformance_text}")

        except Exception as error:
            logging.exception(f"Error in find_conformance of {StatusFinder.__name__}: {str(error)}")
            return False


    def replace_not(self,match):
        try:
            # Define the replacements logic
            inner_text = match.group(1)
            for symbol, replacement in self.REPLACEMENTS_LOGIC.items():
                if symbol in inner_text:
                    inner_text = inner_text.replace(symbol, replacement)
            return f"NOT ({inner_text})"
        except Exception as error:
            logging.exception(f"Error in replace_not: {str(error)}")
            return match.group(0)  # Return the original match if an error occurs
    def format_replacements(self,conformance_text):
        try:
            # Apply the custom logic for '!'
            conformance_text = re.sub(r'!\(([^)]+)\)', self.replace_not, conformance_text)
            conformance_text = re.sub(r'!(\w+(\.\w+)*)', r'NOT (\1)', conformance_text)

            # Replace the remaining symbols
            for symbol, replacement in self.REPLACEMENTS_LOGIC.items():
                if symbol != "!":
                    conformance_text = conformance_text.replace(symbol, replacement)

            return conformance_text
        except Exception as error:
            logging.exception(f"Error in format_replacements: {str(error)}")
            return conformance_text

    def process_segment(self,segment):
        try:
            # Remove content within parentheses
            pattern_remove_parens = r"\([^\)]+\)"
            segment_no_parens = re.sub(pattern_remove_parens, '', segment)
            return segment_no_parens.strip()
        except Exception as error:
            logging.exception(f"Error in process_segment: {str(error)}")
            return segment

    def handle_segment(self,segment):
        try:

            validation_pattern = r"^(\[|)[A-Z]+\.[CS]\.([FCE]\d{2}|A\d{4})(\(|\.(Rsp|Tx)\()"
            # If segment matches the validation pattern, process it
            if re.match(validation_pattern, segment):
                return self.process_segment(segment)
            else:
                return segment
        except Exception as error:
            logging.exception(f"Error in handle_segment: {str(error)}")
            return segment

    def reformat_conformance_text(self,conformance_text):
        try:
            # Apply format replacements before processing
            conformance_text = self.format_replacements(conformance_text)

            # Split the input by '|' and '&' to handle each segment individually
            separators = r'[|&]'
            segments = re.split(f'({separators})', conformance_text)

            # Process each segment
            processed_segments = []
            for segment in segments:
                if re.match(separators, segment):
                    processed_segments.append(segment)  # Keep separators as is
                else:
                    # Apply processing only to segments that match the pattern
                    processed_segments.append(self.handle_segment(segment))

            # Join the processed segments with their original separators
            reformatted_text = ''.join(processed_segments)



            return reformatted_text
        except Exception as error:
            logging.exception(f"Error in reformat_conformance_text: {str(error)}")
            return conformance_text

    def process_o_a_plus(self, pics, pics_pixit_type, o_a_pics_list, conformance_text):
        try:
            st_conformance = []
            st_text = []
            if conformance_text=='O.b+':
                pass
            if conformance_text not in self.pics_pixit_count[pics_pixit_type]:
                self.pics_pixit_count[pics_pixit_type][conformance_text]=0

            self.pics_pixit_count[pics_pixit_type][conformance_text] += 1
            # self.pics_pixit_count[pics_pixit_type]['O.a+'] += 1
            pics_feature_list = []
            for pics_name in o_a_pics_list:
                if pics.split("(")[0] != pics_name:
                    pics_feature_list.append(pics_name)
            if len(pics_feature_list) == 1:
                st_conformance.append("M")
                st_text.append("NOT (" + pics_feature_list[0] + " )")
            elif len(pics_feature_list) > 1:
                st_conformance.append("M")
                str_pics_text = " "
                for pics_text in pics_feature_list:
                    if str_pics_text != " ":
                        str_pics_text = str_pics_text + " AND "
                    str_pics_text = (str_pics_text + "(NOT (" + pics_text + "))").strip()
                st_text.append(str_pics_text)
            if '+' in conformance_text:
            # if conformance_text == "O.a+":
                st_conformance.append("O")
                option_pics_text = " "
                for pics_text in pics_feature_list:
                    if option_pics_text != " ":
                        option_pics_text = option_pics_text + " OR "
                    option_pics_text = (option_pics_text + pics_text).strip()
                st_text.append(option_pics_text)

            return st_conformance, st_text
        except Exception as error:
            logging.exception(f"Error in process_o_a_plus of {StatusFinder.__name__}: {str(error)}")
            return False
