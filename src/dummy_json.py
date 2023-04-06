import logging
import requests
from digitalai.release.integration import BaseTask

logger = logging.getLogger('Digitalai')


class DummyJson(BaseTask):
    """
        The purpose of this task is to fetch product details from a remote server by product ID.
    """
    def execute(self) -> None:
        product_name = None
        product_brand = None
        try:
            # Process input properties
            if not self.input_properties['server']:
                raise ValueError("Server field cannot be empty")
            else:
                server = self.input_properties['server']
            server_url = server['url'].strip("/")
            auth = (server['username'], server['password'])
            request_url = server_url + "/products/" + self.input_properties['productId']

            # Make request
            self.add_comment(f"Sending request to {request_url}")
            response = requests.get(request_url, auth=auth)
            response.raise_for_status()

            # Process result
            product_name = response.json()['title'].strip()
            product_brand = response.json()['brand'].strip()
        except Exception as e:
            logger.error("Unexpected error occurred.", exc_info=True)
            self.set_exit_code(1)
            self.set_error_message(str(e))
        finally:
            self.set_output_property('productName', product_name)
            self.set_output_property('productBrand', product_brand)
