import re
import logging


class TagSeparator:
    @staticmethod
    def separate_tag(doc_text):
        """
        Separates the tag number and tag name from the given document text.

        Args:
            doc_text (str): The document text.

        Returns:
            tuple: A tuple containing the tag number and tag name.
        """
        try:
            '''
            class_name = TagSeparator.__name__
            method_name = "separate_tag"
            logging.info(f"Executing {method_name} in {class_name}")
            '''
            # Define the regular expression pattern to split the tag number and tag name
            REGEX_split_no = r"(?P<No>^[\d]+[\d\.]*)(?P<Name>.*)"

            # Find all matches of the pattern in the document text
            match_level1 = re.finditer(REGEX_split_no, doc_text)

            tag_name = None
            tag_no = None

            # Iterate over the matches and extract the tag number and tag name
            for match in match_level1:
                tag_name = match.group("Name").strip()
                tag_no = match.group("No").strip()

            return tag_no, tag_name
        except Exception as e:
            class_name = TagSeparator.__name__
            method_name = "separate_tag"
            logging.exception(f"Error in {method_name} of {class_name}: {str(e)}")
