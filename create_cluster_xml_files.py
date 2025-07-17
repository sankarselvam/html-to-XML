import datetime
import logging
import os
import re
import time
import xml.etree.ElementTree as et
import xml.sax.saxutils as su

from tp_data_classes import LinePlacement, PicsXmlData


class CreateClusterXmlFiles:
    def __init__(
            self,
            xml_dict,
            rev_data,
            xml_file_path,
            mcore_cluster_list,
            combined_mcore_pics,
            version_no="V_18"
    ):
        try:
            self.is_pics_present = False
            self.obj_xml_data = xml_dict
            self.obj_rev_data = rev_data
            self.mcore_cluster_list = mcore_cluster_list
            self.combined_mcore_pics = combined_mcore_pics
            self.version_no = version_no

            time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime(
                "%Y_%m_%d_%H_%M_%S"
            )
            self.report_folder = "XML_" + self.obj_rev_data.rev_number.replace(",", "")
            self.report_folder = os.path.join("OutputXML", self.report_folder)

            self.report_folder = os.path.join(xml_file_path, self.report_folder)
            if not os.path.exists(self.report_folder):
                os.makedirs(self.report_folder)
        except Exception as error:
            logging.exception(f"Error in initialization of {CreateClusterXmlFiles.__name__}: {str(error)}")

    def write_file(self):
        try:
            # cluster file write
            for cluster in self.obj_xml_data.keys():
                if cluster not in self.mcore_cluster_list or cluster in self.combined_mcore_pics:
                    if cluster in self.combined_mcore_pics:
                        a=1

                    self.is_pics_present = False
                    self.single_file_write(cluster, self.obj_xml_data[cluster])
            # Base xml write
            mcore_dict, pixit_dict = self.extract_mcore_data()
            is_base = True
            self.single_file_write("Base", mcore_dict, is_base)
            a = 1

        except Exception as error:
            logging.exception(f"Error in write_file of {CreateClusterXmlFiles.__name__}: {str(error)}")

    def extract_mcore_data(self):
        try:
            mcore_dict = {}
            pixit_dict = {}
            variable = None,
            description = None,
            mandatory_optional = None,
            notes_additional = None,
            reference = None
            # Matter Software Component Policy
            obj_pics_xml_data = PicsXmlData("MCORE.DT_SW_COMP", "Is DUT Software Component?", "O", " ",
                                            "Matter Software Component Policy")
            obj_pics_xml_data.pics = obj_pics_xml_data.variable
            obj_pics_xml_data.status_conformance.append("O")
            obj_pics_xml_data.status_text.append("")
            mcore_dict[obj_pics_xml_data.variable] = obj_pics_xml_data

            for item in self.mcore_cluster_list:
                data = self.obj_xml_data[item]
                mcore = data.mcore
                pixit = data.pixit

                for key, value in mcore.items():
                    if key not in mcore_dict:
                        mcore_dict[key] = value

                for key, value in pixit.items():
                    if key not in pixit_dict:
                        pixit_dict[key] = value

            return mcore_dict, pixit_dict
        except Exception as error:
            logging.exception(f"Error occurred in CreateClusterXmlFiles.extract_mcore_data: {str(error)}")
            return False

    def single_file_write(self, cluster_name, cluster_data, is_base=False):
        try:
            logging.info(f"CreateXmlFile _ {cluster_name} is started")
            ns = {"xsi": "http://www.w3.org/2001/XMLSchema-instance"}
            comment_text = self.comments_write_text(cluster_name)
            cluster_element = "clusterPICS"
            if is_base:
                cluster_element = "generalPICS"

            cluster_pics = et.Element(cluster_element)
            cluster_pics.set(
                et.QName(ns["xsi"], "noNamespaceSchemaLocation"),
                "Generic-PICS-XML-Schema.xsd",
            )  # Add xsi:schemaLocation attribute

            # Create the comment element
            comment = et.Comment(comment_text)

            # Add the comment element as the first child of cluster_pics
            cluster_pics.insert(0, comment)

            if is_base:
                self.mcore_pics_write(cluster_data, cluster_pics)
            else:
                # Invoke general_cluster_write method
                self.general_cluster_write("General cluster information", cluster_pics, cluster_data)

                # Invoke cluster_role_write method
                self.cluster_role_write("Cluster role information", cluster_pics, cluster_data.role)

                self.cluster_pics_write(cluster_data, cluster_pics)

            # Serialize the XML tree to a string with auto-generated XML declaration
            xml_string = et.tostring(cluster_pics, encoding="unicode", xml_declaration=True)

            # Create XML string with proper formatting
            formatted_xml_string = "\n".join(line for line in xml_string.splitlines() if line.strip())
            tags_to_format = [
                "<!--",
                "</clusterPICS>",
                "<clusterId>",
                "<picsRoot>",
                "<picsItem>",
                "<feature>",
                "<reference>",
                "<status",
                "<support>",
                "</picsItem>",
                "</usage>",
                "</attributes>",
                "</events>",
                "</commandsReceived>",
                "</features>",
                "</commandsGenerated>",
                "</manually>",
                "</clusterSide",
                "<pixit>",
                "<pixit />",
                "<pixitItem>",
                "</pixit>",
                "</pixitItem>",
                "</generalPICS>",
                "<pics label=",
                "<itemNumber"
            ]
            for tag in tags_to_format:
                formatted_xml_string = self.format_xml_string(formatted_xml_string, tag)
            formatted_xml_string = self.format_xml_string(formatted_xml_string, "-->", LinePlacement.ENDING)

            formatted_xml_string = self.tab_format_xml_string(formatted_xml_string)
            lines = formatted_xml_string.split('\n')
            lines.insert(11, lines.pop(1))
            modified_lines = [line.lstrip() for line in lines[:11]] + lines[11:]
            modified_xml_string = '\n'.join(modified_lines)
            modified_xml_string = modified_xml_string.replace("\n\n", "\n").replace("\n\t\n", "\n")
            cluster_name = re.sub(r"/", "-", cluster_name, flags=re.IGNORECASE)
            file_name = cluster_name + ".xml"
            full_name = os.path.join(self.report_folder, file_name)
            if cluster_name == "Unit Localization Cluster Test Plan":
                a = 1
            # modified_xml_string = modified_xml_string.replace("&amp;", "&")
            # occurrence_count = modified_xml_string.count("&amp;")
            if self.is_pics_present:
                with open(full_name, "w", encoding="utf-8") as file:
                    file.write(modified_xml_string)
                logging.info(f"CreateXmlFile _ {cluster_name} is finished")
            else:
                logging.info(f"CreateXmlFile _ {cluster_name} is not finished")

        except Exception as error:
            logging.exception(f"Error in single_file_write of {CreateClusterXmlFiles.__name__}: {str(error)}")

    @staticmethod
    def tab_format_xml_string(xml_string):
        lines = xml_string.splitlines()
        formatted_lines = []

        indent = -1
        formatted_line = ''
        for line in lines:

            stripped_line = line.strip()
            formatted_line = "\t" * indent + line.strip()
            '''
            # Regular expression pattern
            pattern = r"^<[^<].*[^<]$"

            # Check if the stripped_line matches the pattern
            if re.match(pattern, stripped_line):
                # Match found, execute the code
            '''
            if stripped_line.startswith("<") and not stripped_line.startswith("<!") and not stripped_line.__contains__(
                    "</") and not stripped_line.__contains__("/>"):
                indent += 1
            if stripped_line.startswith("</"):
                indent -= 1
                formatted_line = "\t" * indent + line.strip()

            formatted_lines.append(formatted_line)

        return "\n".join(formatted_lines)

    @staticmethod
    def format_xml_string(xml_string, replace_name, line_placement=LinePlacement.STARTING):
        try:
            if line_placement == LinePlacement.STARTING:
                formatted_xml_string = xml_string.replace(replace_name, "\n" + replace_name)
            elif line_placement == LinePlacement.ENDING:
                formatted_xml_string = xml_string.replace(replace_name, replace_name + "\n")
            else:
                formatted_xml_string = xml_string
            return formatted_xml_string
        except Exception as error:
            logging.error(f"Error in format_xml_string of {CreateClusterXmlFiles.__name__}: {str(error)}")

    def disable_for_debug(self, disable):
        if disable:
            self.obj_rev_data.date = "Disabled for Debug"
            self.obj_rev_data.rev_number = "Disabled for Debug"
            self.obj_rev_data.rev_remark = "Disabled for Debug"
            self.obj_rev_data.rev_date = "Disabled for Debug"

    def comments_write(self, pics_code, cluster_name):
        try:
            self.disable_for_debug(False)
            # self.disable_for_debug(False)
            '''
            text_comment = (
                f"\n Autogenerated xml file \n   Generated date:{self.obj_rev_data.date} \n   Version No:{self.version_no} \n Cluster Name -{cluster_name}\n "
                f"XML PICS -Ref Document: \n      {self.obj_rev_data.rev_number}\n      {self.obj_rev_data.rev_remark} \n      {self.obj_rev_data.rev_date} \n"
            )
            '''
            text_comment = """
                    Autogenerated xml file
                    Generated date:{date}
                    Version No:{version}
                    Cluster Name -{cluster_name}
                    XML PICS -Ref Document:
                    {rev_number}
                    {rev_remark}
                    {rev_date}
                    """.format(
                date=self.obj_rev_data.date,
                version=self.version_no,
                cluster_name=cluster_name,
                rev_number=self.obj_rev_data.rev_number,
                rev_remark=self.obj_rev_data.rev_remark,
                rev_date=self.obj_rev_data.rev_date,
            )
            comment = et.Comment(text_comment)
            pics_code.append(comment)
        except Exception as error:
            logging.exception(f"Error in comments_write of {CreateClusterXmlFiles.__name__}: {str(error)}")

    def comments_write_text(self, cluster_name):
        try:
            # self.disable_for_debug(False)
            self.disable_for_debug(False)
            text_comment = """
                    Autogenerated xml file - Version No:{version}
                    Generated date:{date}                    
                    Cluster Name -{cluster_name}
                    XML PICS -Ref Document:
                    {rev_number}
                    {rev_remark}
                    {rev_date}
                    """.format(
                date=self.obj_rev_data.date,
                version=self.version_no,
                cluster_name=cluster_name,
                rev_number=self.obj_rev_data.rev_number,
                rev_remark=self.obj_rev_data.rev_remark,
                rev_date=self.obj_rev_data.rev_date,
            )
            return text_comment
        except Exception as error:
            logging.exception(f"Error in comments_write of {CreateClusterXmlFiles.__name__}: {str(error)}")

    @staticmethod
    def general_cluster_write(cmd_msg, cluster_code, cluster_data):
        try:
            formatted_string = """
                            Notes:

                                - PICS definition table contains PICS from other clusters that may be needed to run all the test cases.
                                - To load these PICS, refer to the following clusters.                                
                                {:<50} {:<50} {:<50}                                
                           """.format("PICS", "Cluster Name", "Reference")
            if len(cluster_data.other_cluster_pics) > 0:

                for pics in cluster_data.other_cluster_pics:
                    cluster_name=cluster_data.other_cluster_pics[pics].cluster
                    ref_text = cluster_data.other_cluster_pics[pics].reference
                    formatted_string += f"\n {pics:<50} {cluster_name:<50} {ref_text:<50}"
                    # formatted_string += f"\n                                {pics:<50} {cluster_name:<50} {ref_text:<50}"
                cmd_msg = cmd_msg + formatted_string+f"\n"

            comment = et.Comment(cmd_msg)
            cluster_code.append(comment)

            name = et.Element("name")
            name.text = cluster_data.cluster_name
            cluster_code.append(name)

            cluster_id = et.Element("clusterId")
            cluster_id.text = " "
            cluster_code.append(cluster_id)

            pics_code = et.Element("picsRoot")
            pics_code.text = " "
            cluster_code.append(pics_code)

        except Exception as error:
            logging.error(f"Error in general_cluster_write of {CreateClusterXmlFiles.__name__}: {str(error)}")

    def cluster_role_write(self, cmd_msg, cluster_code, usage_data):
        try:
            comment = et.Comment(cmd_msg)
            cluster_code.append(comment)

            usage = et.Element("usage")
            for name in usage_data:
                item = usage_data[name]
                pics_item = et.Element("picsItem")

                itemNumber = et.Element("itemNumber")
                itemNumber.text = item.variable
                pics_item.append(itemNumber)

                feature = et.Element("feature")
                feature.text = item.description
                pics_item.append(feature)

                reference = et.Element("reference")
                reference.text = item.reference
                if reference.text is None or reference.text == '':
                    reference.text = " MATTER"
                # reference.text = " MATTER"
                pics_item.append(reference)

                status = et.Element("status")
                status.text = item.mandatory_optional
                status.text = "O"
                pics_item.append(status)

                support = et.Element("support")
                support.text = "false"
                pics_item.append(support)

                usage.append(pics_item)
                self.is_pics_present = True

            cluster_code.append(usage)

        except Exception as error:
            logging.error(f"Error in cluster_role_write of {CreateClusterXmlFiles.__name__}: {str(error)}")

    def cluster_pics_write(self, xml_data, cluster_code):
        try:

            pixit_data = xml_data.pixit
            comment = et.Comment(f"PIXIT")
            cluster_code.append(comment)
            pics_head = et.Element("pixit")
            if pixit_data and len(pixit_data) > 0:
                for pixit, obj_pics_xml_data in pixit_data.items():
                    pixit_item = self.pics_item_write(obj_pics_xml_data, "pixitItem")
                    pics_head.append(pixit_item)

            cluster_code.append(pics_head)
            for server_client, data in xml_data.serverclient.items():
                server_client_values = list(data.data.keys())
                comment = et.Comment(f"{server_client.value} side PICS")
                cluster_code.append(comment)
                pics_server_head = et.Element("clusterSide", type=server_client.value)
                for pic_type in server_client_values:
                    pic_type_name_0 = pic_type.value[0]
                    pic_type_name_1 = pic_type.value[1]

                    pic_data = data.data.get(pic_type)
                    comment = et.Comment(f"{pic_type_name_0} PICS write")
                    pics_server_head.append(comment)
                    pics_head = et.Element(pic_type_name_1)
                    if pic_data and len(pic_data) > 0:
                        for pics, obj_pics_xml_data in pic_data.items():
                            self.is_pics_present = True
                            pics_item = self.pics_item_write(obj_pics_xml_data)
                            pics_head.append(pics_item)
                    pics_server_head.append(pics_head)
                cluster_code.append(pics_server_head)

        except Exception as error:
            logging.error(f"Error in cluster_pics_write of {CreateClusterXmlFiles.__name__}: {str(error)}")
            return None

    def mcore_pics_write(self, mcore_data, cluster_code):
        try:

            comment = et.Comment("Mcore PICS")
            cluster_code.append(comment)
            name = et.Element("name")
            name.text = "Base"
            cluster_code.append(name)
            pics_mcore_head = et.Element("pics", label="Base Details")
            for pics, obj_pics_xml_data in mcore_data.items():
                self.is_pics_present = True
                pics_item = self.pics_item_write(obj_pics_xml_data)
                pics_mcore_head.append(pics_item)
            cluster_code.append(pics_mcore_head)
        except Exception as error:
            logging.error(f"Error in mcore_pics_write of {CreateClusterXmlFiles.__name__}: {str(error)}")
            return None

    @staticmethod
    def pics_item_write(item, pics_pixit_name="picsItem"):
        try:
            if item == "LUNIT.TempUnit.Kelvin":
                a = 1
            pics_item = et.Element(pics_pixit_name)

            itemNumber = et.Element("itemNumber")
            itemNumber.text = item.pics
            pics_item.append(itemNumber)

            feature = et.Element("feature")
            # feature.text = item.description
            feature.text = su.escape(item.description)
            if feature.text == "Does the device support the TemperatureUnit Fahrenheit ?":
                a = 1
            pics_item.append(feature)

            reference = et.Element("reference")
            reference.text = item.reference
            if reference.text == "111.2.3. Enums & Values":
                a = 1
            pics_item.append(reference)

            if item.status_text is not None:
                for status_text, status_conformance in zip(item.status_text, item.status_conformance):
                    if status_text != "":
                        status = et.Element("status", cond=status_text)
                    else:
                        status = et.Element("status")

                    status.text = status_conformance
                    pics_item.append(status)
            else:
                status = et.Element("status")
                status.text = "O"
                pics_item.append(status)

            support_text = "false"
            if pics_pixit_name == "pixitItem":
                support_text = "0x00"
            support = et.Element("support")
            support.text = support_text
            pics_item.append(support)

            return pics_item
        except Exception as error:
            logging.error(f"Error in pics_item_write of {CreateClusterXmlFiles.__name__}: {str(error)}")
