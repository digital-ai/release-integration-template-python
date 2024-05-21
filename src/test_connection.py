import requests
from digitalai.release.integration import BaseTask


class TestConnection(BaseTask):
    """
        Testing connection to the remote server
    """
    def execute(self) -> None:

        try:
            # Process input
            server = self.input_properties['server']
            server_url = server['url'].strip("/")
            auth = (server['username'], server['password'])

            # Make request
            response = requests.get(server_url, auth=auth)
            response.raise_for_status()

            # Process result
            result = {"success": True, "output": "Connection success"}
        except Exception as e:
            result = {"success": False, "output": str(e)}
        finally:
            self.set_output_property("commandResponse", result)
