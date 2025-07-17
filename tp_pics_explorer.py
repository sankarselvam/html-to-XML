import copy
import logging
from collections import OrderedDict, defaultdict
from io import StringIO
from typing import Optional
import pandas as pd

from tag_separator import TagSeparator
from tp_data_classes import DictPicsPixit, TableXmlData, TableDataTagId, PicsPixitType


class TpPicsExplorer:
    """
    Class for exploring TP pics data.
    """

    columns_list = []  # Define the columns_list attribute

    def explore(self, pics_pixit_id, all_tag_data,html_info_dict):

        try:

            logging.info(f"Executing explore in {self.__class__.__name__}")

            # Initialize an ordered dictionary to store PICS and PIXIT data for each cluster
            pics_pixit_data = OrderedDict()

            # Iterate over each plan and cluster in the pics_pixit_id dictionary
            for plan_name in pics_pixit_id:
                doc_name=html_info_dict[plan_name]['DocumentName']
                for cluster in pics_pixit_id[plan_name]:
                    # Create a DictPicsPixit instance to store PICS and PIXIT data for the current cluster
                    pics_pixit_data[cluster] = DictPicsPixit()

                    # Get the HTML tag data for the current plan
                    html_tag_data = all_tag_data[plan_name]

                    # Extract the PICS IDs for the current cluster
                    pics_id_list = pics_pixit_id[plan_name][cluster].pics_id_list
                    if pics_id_list:
                        pics_dict = self.load_pics_tags(pics_id_list, html_tag_data,doc_name)
                        if pics_dict is False:
                            # Handle the false condition here
                            logging.debug(
                                f"{cluster}-PICS Id- Return False-Error in {TpPicsExplorer.__name__}:load_pics_tags ")
                            continue
                        pics_pixit_data[cluster].pics_dict = pics_dict
                    else:
                        logging.debug(f"No PICS definition table  :  {cluster}")

                    # Extract the PIXIT IDs for the current cluster
                    pixit_id_list = pics_pixit_id[plan_name][cluster].pixit_id_list
                    if pixit_id_list:
                        pixit_dict = self.load_pics_tags(pixit_id_list, html_tag_data,doc_name)
                        if pixit_dict is False:
                            logging.debug(
                                f"{cluster}-PIXIT Id- Return False-Error in {TpPicsExplorer.__name__}:load_pics_tags ")
                            continue
                        pics_pixit_data[cluster].pixit_dict = pixit_dict
                    else:
                        logging.debug(f"No PIXIT definition table :  {cluster} ")

            pics_pixit_table_data = self.read_pics_tags(pics_pixit_data)
            self.find_columns()
            if pics_pixit_table_data is False:
                # Handle the false condition here
                logging.debug(f"Return False-Error in {TpPicsExplorer.__name__}:read_pics_tags")

            return pics_pixit_table_data

        except Exception as error:
            # Log the exception details as an error
            logging.exception(f"Error in explore of {TpPicsExplorer.__name__}: {str(error)}")
            return False

    def find_columns(self):
        try:
            unique_columns = list(map(list, set(map(tuple, self.columns_list))))

            logging.info(f"Table column heading details and used count")
            for column in unique_columns:
                print(column)

            similarity_counts = defaultdict(int)

            for column in self.columns_list:
                column_key = tuple(column)
                similarity_counts[column_key] += 1

            for column, count in similarity_counts.items():
                logging.debug(
                    f"{list(column)} - {count} tables")

        except Exception as error:
            logging.exception(f"Error in find_columns of {TpPicsExplorer.__name__}: {str(error)}")
            return False

    @staticmethod
    def load_pics_tags(pics_id_list, html_tag_data,doc_name):
        """
        Load PICS tags based on the provided ID list and tag data.

        Args:
            pics_id_list (list): List of PICS IDs.
            html_tag_data (dict): Dictionary of tag data.

        Returns:
            OrderedDict: Loaded PICS tags.
        """
        try:
            s_no_heading = 1
            pics_dict = OrderedDict()
            # logging.info(f"Executing load_pics_tags in {self.__class__.__name__}")
            if len(pics_id_list) > 0:
                for pics_id in pics_id_list:
                    if pics_id == '20.':
                        a = 1
                    tag_pic = html_tag_data[pics_id].doc
                    tag_pic_with_name = tag_pic.find('h2')
                    tag_id_with_name = pics_id
                    if tag_pic_with_name is not None:
                        tag_id_with_name = tag_pic_with_name.text+ " - "+doc_name

                    table_data_pic = tag_pic.find_all("table")
                    if len(table_data_pic) > 0:
                        for table_no in range(len(table_data_pic)):
                            html_str = str(table_data_pic[table_no])  # Convert to string explicitly
                            pd_df = pd.read_html(StringIO(html_str), header=0)[0].fillna(" ")
                            #pd_df = pd.read_html(str(table_data_pic[table_no]), header=0)[0].fillna(" ")
                            is_not_found = True
                            obj_table_tag_id = TableDataTagId(tag_id_with_name, pd_df)
                            child_tag = table_data_pic[table_no].find_previous_sibling(
                                ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

                            if child_tag is not None:
                                tag_head = child_tag.name
                                child_tag_id, child_table_heading = TagSeparator.separate_tag(child_tag.text)
                                obj_table_tag_id.tag_id = child_tag.text+ " - "+doc_name
                                if tag_head[1:].isdigit():
                                    parent_head = 'h' + str(int(tag_head[1:]) - 1)
                                    parent_tag = child_tag.parent.find_parent("div").find(parent_head)
                                    if parent_tag is not None:
                                        parent_tag_id, parent_table_heading = TagSeparator.separate_tag(parent_tag.text)
                                        if parent_table_heading not in pics_dict:
                                            pics_dict[parent_table_heading] = OrderedDict()
                                        elif not isinstance(pics_dict[parent_table_heading],
                                                            OrderedDict):
                                            logging.debug(f"Already defined in Dict{parent_table_heading}")

                                        # Check if the child table heading exists in the parent table dictionary
                                        if isinstance(pics_dict[parent_table_heading], OrderedDict):
                                            if child_table_heading not in pics_dict[parent_table_heading]:
                                                pics_dict[parent_table_heading][child_table_heading] = []

                                            pics_dict[parent_table_heading][child_table_heading].append(
                                                obj_table_tag_id)
                                            s_no_heading += 1
                                        else:
                                            if child_table_heading not in pics_dict:
                                                pics_dict[child_table_heading] = []
                                            pics_dict[child_table_heading].append(obj_table_tag_id)
                                    else:
                                        if child_table_heading not in pics_dict:
                                            pics_dict[child_table_heading] = []
                                        pics_dict[child_table_heading].append(obj_table_tag_id)
                                    s_no_heading += 1
                            else:
                                pics_dict["Table No:" + str(s_no_heading)] = []
                                pics_dict["Table No:" + str(s_no_heading)].append(obj_table_tag_id)
                                s_no_heading += 1

            return pics_dict
        except Exception as error:
            logging.exception(f"Error in load_pics_tag of {TpPicsExplorer.__name__}: {str(error)}")
            return False

    def read_pics_tags(self, pics_pixit_data):
        """
        Read PICS tags from the provided data.

        Args:
            pics_pixit_data (OrderedDict): Cluster data containing pics and pixit dictionaries.

        Returns:
            OrderedDict: Table data containing the read pics and pixit dictionaries.
        """
        try:
            logging.info(f"Executing read_pics_tag in {self.__class__.__name__}")
            # Create an empty OrderedDict to store the table data
            pics_table_data = OrderedDict()
            # Iterate over each cluster and its corresponding data
            for cluster, data in pics_pixit_data.items():
                # Create an entry in pics_table_data for the current cluster
                pics_table_data[cluster] = DictPicsPixit()

                # Read the pics dictionary for the current cluster
                pics_dict = data.pics_dict
                pics_table_data[cluster].pics_dict = self.read_cluster_pics(
                    pics_dict, cluster, PicsPixitType.PICS.value
                )

                # Read the pixit dictionary for the current cluster
                pixit_dict = data.pixit_dict
                pics_table_data[cluster].pixit_dict = self.read_cluster_pics(
                    pixit_dict, cluster, PicsPixitType.PIXIT.value
                )

            # Return the table data containing the read pics and pixit dictionaries
            return pics_table_data

        except Exception as error:
            logging.exception(f"Error in read_pics_tag of {TpPicsExplorer.__name__}: {str(error)}")
            return False

    def read_cluster_pics(self, pics_dict, cluster, pics_type):
        """
        Read the cluster pics data.

        Args:
            pics_dict (OrderedDict): Dictionary containing the pics data.
            cluster (str): Name of the cluster.
            pics_type (str): Type of the pics data (Pics or Pixit).

        Returns:
            OrderedDict: Table data containing the read pics data.
        """
        try:
            # logging.info(f"Executing read_cluster_pics in {self.__class__.__name__}")

            # Using copy.copy() to create a shallow copy
            pics_table_data = copy.copy(pics_dict)

            # Iterate over each parent heading in the pics dictionary
            for parent_heading, child_heading_or_tag_list in pics_dict.items():
                # Check if the parent heading is an OrderedDict (indicating nested data)
                if isinstance(child_heading_or_tag_list, OrderedDict):
                    # Iterate over each child heading within the nested OrderedDict
                    for child_heading, tag_list in child_heading_or_tag_list.items():
                        pics_table_data[parent_heading][child_heading] = []
                        # Load the pics row and create an instance of TableXmlData
                        concatenated_heading = f"{parent_heading} - {child_heading}"
                        obj_pics_xml_data = self.load_pics_row(
                            tag_list[0], concatenated_heading, cluster, pics_type
                        )
                        if obj_pics_xml_data is False:
                            logging.debug(
                                f"Skipping:Unable to read the table:- {cluster}:{parent_heading}-{child_heading}")
                            continue
                        pics_table_data[parent_heading][child_heading].append(obj_pics_xml_data)

                else:
                    tag_list = child_heading_or_tag_list
                    pics_table_data[parent_heading] = []
                    # Load the pics row and create an instance of TableXmlData
                    obj_pics_xml_data = self.load_pics_row(
                        tag_list[0], str(parent_heading), cluster, pics_type
                    )
                    if obj_pics_xml_data is False:
                        logging.debug(f"Skipping:Unable to read the table :- {cluster}:{parent_heading}")
                        continue
                    pics_table_data[parent_heading].append(obj_pics_xml_data)

            # Return the table data containing the read pics data
            return pics_table_data

        except Exception as error:
            logging.exception(f"Error in read_cluster_pics of {TpPicsExplorer.__name__}: {str(error)}")
            return False

    def load_pics_row(self, table_data_tag_id: TableDataTagId, pics_head: str, cluster_name: str, pics_type: str) -> \
            Optional[TableXmlData]:
        """
        Load the pics row data.

        Args:
            data_frame (DataFrame): DataFrame containing the pics row data.
            pics_head (str): Heading of the pics data.
            cluster_name (str): Name of the cluster.
            pics_type (str): Type of the pics data (Pics or Pixit).

        Returns:
            Optional[TableXmlData]: Instance of TableXmlData containing the loaded pics row data, or None if an error occurs.
            :param cluster_name:
            :param pics_head:
            :param table_data_tag_id:
        """
        try:
            data_frame = table_data_tag_id.pd_df
            self.columns_list.append(data_frame.columns.tolist())
            if ['#', 'Variable', 'Description', 'Mandatory/Optional',
                'Notes/Additional Constraints'] == data_frame.columns.tolist():
                a = 1
            if ['Variable', 'Description', 'Unnamed: 2', 'Mandatory/Optional',
                'Notes/Additional Constraints'] == data_frame.columns.tolist():
                a = 1
            obj_pics_xml_data = TableXmlData(table_data_tag_id.tag_id)  # Create an instance of TableXmlData

            column_names = data_frame.columns.values  # Get the column names of the DataFrame

            # Check if the required columns are present in the DataFrame
            required_columns = ["Variable", "Description", "Mandatory/Optional", "Notes/Additional Constraints"]
            required_columns_types = [
                required_columns,  # Added the required_columns as a separate type
                ['Variable', 'Description', 'Mandatory/Optional', 'Notes/Additional Constraints'],
                ['Variable', 'Device Description', 'Mandatory/Optional', 'Notes'],
                ['#', 'Description', 'Mandatory/Optional', 'Notes/Additional Constraints'],
                ['Variable', 'Description', 'M=Mandatory O=Optional X=disallowed', 'Notes/Additional Constraints'],
                ['Variable', 'Description', 'Conformance', 'Notes/Additional Constraints']
            ]

            for columns_type in required_columns_types:
                if all(col in column_names for col in columns_type):
                    if not all(col in column_names for col in required_columns):
                        logging.debug(f"{columns_type} {cluster_name} - {pics_head}")
                    # Load the data into the TableXmlData instance based on column names
                    obj_pics_xml_data.variable = data_frame.get(columns_type[0])
                    obj_pics_xml_data.mandatory_optional = data_frame.get(columns_type[2])
                    obj_pics_xml_data.description = data_frame.get(columns_type[1])
                    obj_pics_xml_data.notes_additional = data_frame.get(columns_type[3])
                    break

            else:
                if len(column_names) == 4:
                    logging.debug(f"Table Heading Mismatch-{column_names} - {cluster_name} - {pics_head}")
                    '''
                    # Insert a new row with the column names as values
                    data_frame.loc[-1] = column_names
                    data_frame.index = data_frame.index + 1
                    data_frame = data_frame.sort_index()
                    '''
                    # Load the data into the TableXmlData instance from the columns
                    obj_pics_xml_data.variable = data_frame[column_names[0]].values.tolist()
                    obj_pics_xml_data.description = data_frame[column_names[1]].values.tolist()
                    obj_pics_xml_data.mandatory_optional = data_frame[column_names[2]].values.tolist()
                    obj_pics_xml_data.notes_additional = data_frame[column_names[3]].values.tolist()
                else:
                    logging.debug(f"Invalid Table - {len(column_names)} {column_names} - {cluster_name} - {pics_head}")

            return obj_pics_xml_data

        except Exception as error:
            logging.exception(f"Error in load_pics_row of {self.__class__.__name__}: {str(error)}")
            return None
