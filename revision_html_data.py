import datetime
import logging
import time
from tp_data_classes import RevData


class RevisionHtmlData:

    def extract_revision_data(self, html_soup_data):
        """
        Extracts revision data from the HTML soup data.

        Args:
            html_soup_data (dict): The HTML soup data.

        Returns:
            RevData: The extracted revision data as an instance of RevData class.

        Raises:
            Exception: If an error occurs during data extraction.
        """
        try:
            class_name = self.__class__.__name__
            method_name = "extract_revision_data"
            logging.info(f"Executing {method_name} in {class_name}")

            # Log the execution of the method
            logging.info(f"Executing {method_name} in {class_name}")

            revision_data = RevData()
            for spec_data in html_soup_data:
                revision_data = self.load_revision_data(html_soup_data[spec_data])
                break

            return revision_data

        except Exception as error:
            # Handle any exceptions that occur during data extraction
            logging.exception(f"Error in extract_revision_data of {self.__class__.__name__}: {str(error)}")
            raise

    @staticmethod
    def load_revision_data(html_soup):
        """
        Loads revision data from the HTML soup.

        Args:
            html_soup (BeautifulSoup): The HTML soup data.

        Returns:
            RevData: The loaded revision data as an instance of RevData class.

        Raises:
            Exception: If an error occurs during data loading.
        """
        try:
            class_name = RevisionHtmlData.__name__
            method_name = "load_revision_data"
            logging.info(f"Executing {method_name} in {class_name}")

            revision = RevData()
            revision.date = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

            if len(html_soup.find_all("div", class_="details")) > 0:
                span_data = html_soup.find_all("div", class_="details")[0].find_all("span")
                len_span_data = len(span_data)

                if len_span_data > 2:
                    revision.rev_number = span_data[0].text
                    revision.rev_date = span_data[1].text
                    revision.rev_remark = span_data[2].text

            return revision

        except Exception as error:
            # Handle any exceptions that occur during data loading
            logging.exception(f"Error in load_revision_data of {RevisionHtmlData.__name__}: {str(error)}")
            raise
