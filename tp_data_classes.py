import logging
from collections import OrderedDict
from enum import Enum


# region Class RevData

class RevData:
    """
    Class representing revision data.
    """

    def __init__(self, rev_number=None, rev_date=None, rev_remark=None, date=None):
        """
        Initializes a new instance of the RevData class.

        Args:
            rev_number (Any): The revision number.
            rev_date (Any): The revision date.
            rev_remark (Any): The revision remark.
            date (Any): The date.
        """
        try:
            self.rev_number = rev_number
            self.rev_date = rev_date
            self.rev_remark = rev_remark
            self.date = date
        except Exception as error:
            logging.exception(f"Error in RevData of __init__: {str(error)}")


# endregion
# region Class DataCluster
class DataCluster:
    def __init__(self, name, plan_name, pics_id=None, doc=None):
        try:
            self.name = name
            self.pics_id = pics_id  # PICS Definition
            self.tc_details = OrderedDict()
            self.doc = doc
            self.plan_name = plan_name
        except Exception as error:
            logging.exception(f"Error in DataCluster of __init__: {str(error)}")


# endregion

# region Class TestCaseData
class TestCaseData:
    def __init__(
            self,
            test_plan=None,
            cluster=None,
            test_type=None,
            test_no=None,
            test_name=None,
            test_full_name=None,
            tag_id=None,
            hyper_link=None
    ):
        try:
            self.test_plan_name = test_plan
            self.cluster_name = cluster
            self.test_case_type = test_type
            self.test_case_no = test_no
            self.test_case_name = test_name
            self.tc_full_name = test_full_name
            self.tag_id = tag_id
            self.hyper_link = hyper_link
        except Exception as error:
            logging.exception(f"Error in TestCaseData of __init__: {str(error)}")


# endregion


# region Class DataTag

class DataTag:
    """
    Class representing a data tag.
    """

    def __init__(self, value=None, doc=None, id_=None, name=None):
        """
        Initializes a new instance of the DataTag class.

        Args:
            value (Any): The value of the data tag.
            doc (Any): The documentation of the data tag.
            id_ (Any): The ID of the data tag.
            name (Any): The name of the data tag.
        """
        try:
            self.name = name
            self.id = id_
            self.doc = doc
            self.value = value
        except Exception as error:
            logging.exception(f"Error in DataTag of __init__: {str(error)}")


# endregion

# region Class DataPicsPixit

class DataPicsPixit:
    """
    Class representing DataPicsPixit.
    """

    def __init__(self):
        """
        Initializes a new instance of the DataPicsPixit class.

        Args:
            pics_id_list (Any): The PICS ID list.
            pixit_id_list (Any): The PIXIT ID list.
        """
        try:
            self.pics_id_list = []  # PICS Definition
            self.pixit_id_list = []
            self.test_cases_list = []
        except Exception as error:
            logging.exception(f"Error in DataPicsPixit of __init__: {str(error)}")


# endregion

# region Class DictPicsPixit

class DictPicsPixit:
    """
    Class representing DictPicsPixit.
    """

    def __init__(self):

        try:
            self.pics_dict = OrderedDict()  # PICS Definition
            self.pixit_dict = OrderedDict()
        except Exception as error:
            logging.exception(f"Error in DictPicsPixit of __init__: {str(error)}")


# endregion

# region Class TableXmlData

class TableXmlData:
    def __init__(
            self,
            reference_heading=None,
            variable=None,
            description=None,
            mandatory_optional=None,
            notes_additional=None

    ):
        """
        Initialize a PicsXmlData object.

        Args:
            variable (str): Name of the XML data.
            description (str): Description of the XML data.
            mandatory_optional (str): Indication of whether the data is mandatory or optional.
            notes_additional (str): Additional notes about the XML data.
        """
        try:
            # Initialize attributes
            self.reference_heading = reference_heading
            self.variable = variable
            self.description = description
            self.mandatory_optional = mandatory_optional
            self.notes_additional = notes_additional

        except Exception as error:
            logging.exception(f"Error in TableXmlData of __init__: {str(error)}")


# endregion

# region Class TableDataTagId
class TableDataTagId:
    """
    Class representing TableDataTagId.
    """

    def __init__(self, tag_id=None, pd_df=None):
        """
        Initializes a new instance of the TableDataTagId class.

        Args:
            tag_id (Any): The tag_id of the table.
            pd_df (Any): The table content.
        """
        try:
            self.tag_id = tag_id
            self.pd_df = pd_df
        except Exception as error:
            logging.exception(f"Error in TableDataTagId of __init__: {str(error)}")


# endregion

# region Class LinePlacement
class LinePlacement(Enum):
    STARTING = 1
    ENDING = 2


# endregion

# region Class ServerClient
class ServerClient(Enum):
    """
    Enum representing the server and client values.
    """
    SERVER = "Server"
    CLIENT = "Client"


# endregion

# region Class ClusterReference
class ClusterReference:
    def __init__(self, cluster, reference):
        try:
            self.cluster = cluster
            self.reference = reference
        except Exception as error_type:
            logging.error("ClusterReference __init__ error: %s", str(error_type))


# endregion
# region Class XmlData

class XmlData:
    def __init__(self, cluster_name=None):
        """
        Initialize an XmlData object.

        Args:
            cluster_name (str): Name of the cluster.

        Attributes:
            cluster_name (str): Name of the cluster.
            removed_pics: Duplicates PICS removed from serverclient dict details.
            name_ci: Name CI.
            pics_code: Pics code.
            other_cluster_pics: Other cluster PICS used in this cluster
            feature (str): Feature description.
            serverclient (OrderedDict): Dictionary to store ServerClientData objects for the server and client side.
            mcore (OrderedDict): Dictionary to store mcore data.
            role (OrderedDict): Dictionary to store role data.
            pixit (OrderedDict): Dictionary to store pixit data.
            is_both_pics (bool): Flag indicating if both pics are present.
        """
        try:
            self.cluster_name = cluster_name
            self.removed_pics = OrderedDict()
            # self.name_ci = None
            self.pics_code = []
            self.missing_top_pics = []
            self.other_cluster_pics = OrderedDict()
            self.feature_code = OrderedDict((sc, {}) for sc in ServerClient)
            self.nested_dict = OrderedDict(
                (sc, OrderedDict((pics_type, []) for pics_type in AllTypePics)) for sc in ServerClient
            )
            # Initialize self.o_a_pics_head_dict with OrderedDict instances for AllTypePics
            self.o_conformance_dict=  OrderedDict()
            self.o_a_pics_head_dict = OrderedDict(
                (sc, OrderedDict((pics_type, []) for pics_type in AllTypePics)) for sc in ServerClient)

            # Initialize ServerClientData for the server and client side
            self.serverclient = OrderedDict((sc, ServerClientData()) for sc in ServerClient)
            self.mcore = OrderedDict()
            self.role = OrderedDict()
            self.pixit = OrderedDict()
            self.is_both_pics = False
        except Exception as error_type:
            logging.error("XmlData __init__ error: %s", str(error_type))


# endregion

# region Class Heading(Enum)

class Heading(Enum):
    PICS_DEFINITION = "PICS Definition"
    PIXIT_DEFINITION = "PIXIT Definition"
    TEST_CASES = "Test Cases"


# endregion

# region Class PicsPixitType(Enum)
class PicsPixitType(Enum):
    PICS = "Pics"
    PIXIT = "Pixit"


# endregion


# region Class AllClusterSide(Enum)

class AllClusterSide(Enum):
    """
    Enum representing different cluster sides.
    """
    SERVER = 0
    CLIENT = 1
    MCORE = 6
    ROLE = "Role"
    OTHER = 8


# endregion
'''
# region Class AllTypePics(Enum)
class AllTypePics(Enum):
    ATTRIBUTES = "Attributes"
    EVENTS = "Events"
    COMMANDS_GENERATED = "Commands generated"
    COMMANDS_RECEIVED = "Commands received"
    FEATURES = "Features"
    MANUALLY = "Manual controllable"
    MCORE = "MCORE"
    ROLE = "Role"
    OTHER = 8


# endregion
'''


# region Class AllTypePics(Enum)

class AllTypePics(Enum):
    ATTRIBUTES = "Attributes", "attributes"
    EVENTS = "Events", "events"
    COMMANDS_GENERATED = "Commands generated", "commandsGenerated"
    COMMANDS_RECEIVED = "Commands received", "commandsReceived"
    FEATURES = "Features", "features"
    MANUALLY = "Manual controllable", "manually"
    MCORE = "MCORE", "mcore"
    ROLE = "Role", "role"
    OTHER = 8, "other"


# endregion
# region Class ServerClientData
class ServerClientData:
    def __init__(self):
        """
        Initialize a ServerClientData object.
        """
        try:
            # Initialize attributes for storing data
            self.data = {
                AllTypePics.ATTRIBUTES: OrderedDict(),
                AllTypePics.EVENTS: OrderedDict(),
                AllTypePics.COMMANDS_GENERATED: OrderedDict(),
                AllTypePics.COMMANDS_RECEIVED: OrderedDict(),
                AllTypePics.FEATURES: OrderedDict(),
                AllTypePics.MANUALLY: OrderedDict()
            }
        except Exception as error:
            logging.exception(f"Error in ServerClientData of __init__: {str(error)}")


# endregion

# region Class PicsXmlData

class PicsXmlData:
    def __init__(
            self,
            variable=None,
            description=None,
            mandatory_optional=None,
            notes_additional=None,
            reference=None

    ):
        """
        Initialize a PicsXmlData object.

        Args:
            name (str): Name of the XML data.
            description (str): Description of the XML data.
            mandatory_optional (str): Indication of whether the data is mandatory or optional.
            notes_additional (str): Additional notes about the XML data.
        """
        try:
            # Initialize attributes
            self.id = None
            self.pics = None
            self.name = None
            self.commands_type = None
            self.variable = variable
            self.description = description
            self.mandatory_optional = mandatory_optional
            self.notes_additional = notes_additional
            self.reference = reference
            self.status_text = []
            self.status_conformance = []
            '''
            # Determine status conformance and text based on mandatory_optional value
            if mandatory_optional == "M" or mandatory_optional == "O":
                self.status_conformance.append(mandatory_optional)
            elif mandatory_optional == "Optional" or mandatory_optional == ' ' or mandatory_optional == 'O.a+':
                self.status_conformance.append("O")
            else:
                self.status_conformance.append("To Do")
                self.status_text.append(mandatory_optional)
            '''
        except Exception as error:
            logging.exception(f"Error in PicsXmlData of __init__: {str(error)}")


# endregion

# region Class PicsDetails
class PicsDetails:
    def __init__(self, pics, cluster=None, client_server=None, pics_type=None):
        try:
            if cluster is None:
                cluster = ""
            if client_server is None:
                client_server = AllClusterSide.OTHER
            if pics_type is None:
                pics_type = AllTypePics.OTHER
            self.pics = pics
            self.client_server = client_server
            self.cluster = cluster
            self.pics_type = pics_type
            self.file_name = cluster
        except Exception as error:
            logging.exception(f"Error in PicsDetails of __init__: {str(error)}")

# endregion
