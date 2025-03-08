from digitalai.release.integration import BaseTask
from digitalai.release.v1.api.configuration_api import ConfigurationApi
from digitalai.release.v1.model.system_message_settings import SystemMessageSettings


class SetSystemMessage(BaseTask):
    """
        Sets the system message in the Release UI by invoking the API.
    """

    def execute(self) -> None:

        # Get the message from the input properties
        message = self.input_properties['message']

        # Create the REST client to connect to the Configuration API
        configuration_api = ConfigurationApi(self.get_default_api_client())

        # Define parameter object to send through the API client
        system_message = SystemMessageSettings(
            type='xlrelease.SystemMessageSettings',
            id='Configuration/settings/SystemMessageSettings',
            message=message,
            enabled=True,
            automated=False
        )

        # Make the actual rest call to the designated endpoint
        configuration_api.update_system_message(system_message_settings=system_message)

        # Add a line to the comment section in the UI
        self.add_comment(f"System message updated to \"{message}\"")

        # Example for usage of ReleaseAPIClient
        release_api_client = self.get_release_api_client()

        # Step 1: Create a new global variable
        global_variable = {
            "id": None,
            "key": "global.newVar",
            "type": "xlrelease.StringVariable",
            "requiresValue": "false",
            "showOnReleaseStart": "false",
            "value": "new value"
        }
        response = release_api_client.post("/api/v1/config/Configuration/variables/global", json=global_variable)
        response.raise_for_status()
        global_variable_id = response.json()["id"]
        print(f"Global variable created with ID: {global_variable_id}")

        # Step 2: Update the global variable
        update_global_variable = {
            "id": global_variable_id,
            "key": "global.newVar",
            "type": "xlrelease.StringVariable",
            "requiresValue": "false",
            "showOnReleaseStart": "false",
            "value": "updated value"
        }
        response = release_api_client.put(f"/api/v1/config/{global_variable_id}", json=update_global_variable)
        response.raise_for_status()
        print("Global variable updated:", response.json())

        # Step 3: Retrieve the updated global variable
        response = release_api_client.get(f"/api/v1/config/{global_variable_id}")
        response.raise_for_status()
        print("Retrieved global variable:", response.json())

        # Step 4: Delete the global variable
        response = release_api_client.delete(f"/api/v1/config/{global_variable_id}")
        response.raise_for_status()
        print(f"Global variable deleted successfully. Status code: {response.status_code}")

