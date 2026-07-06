import requests
from digitalai.release.integration import BaseTask


class ServerQuery(BaseTask):
    """
        Fetches product details from a remote server
    """

    def execute(self) -> None:

        # Process input
        server = self.input_properties['server']
        if server is None:
            raise ValueError("Server field cannot be empty")
        server_url = server['url'].strip("/")
        auth = (server['username'], server['password'])
        product_id = self.input_properties['productId']
        request_url = f"{server_url}/products/{product_id}"

        # Make request
        self.add_comment(f"Sending request to {request_url}")
        response = requests.get(request_url, auth=auth)
        response.raise_for_status()

        # Process result
        product_name = response.json()['title'].strip()
        product_brand = response.json()['brand'].strip()
        self.add_comment(f"Product `{product_id}`: {product_name} by {product_brand}")
        self.set_output_property('productName', product_name)
        self.set_output_property('productBrand', product_brand)

