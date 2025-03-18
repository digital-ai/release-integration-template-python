from digitalai.release.integration import BaseTask


class SetSystemMessage(BaseTask):
    """
        Sets the system message using the Release API client.
    """

    def execute(self) -> None:

        # Get the message from the input properties
        message = self.input_properties['message']

        # Obtain an instance of the Release API client
        release_api_client = self.get_release_api_client()

        # Prepare the payload for the API request
        system_message = {
            "type": "xlrelease.SystemMessageSettings",
            "id" : "Configuration/settings/SystemMessageSettings",
            "message": message,
            "enabled": "True",
            "automated": "False"
        }

        # Send a PUT request to update the system message configuration
        release_api_client.put("/api/v1/config/system-message", json=system_message)

        # Add a line to the comment section in the UI
        self.add_comment(f"System message updated to \"{message}\"")

        # Additional examples for usage of ReleaseAPIClient

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

