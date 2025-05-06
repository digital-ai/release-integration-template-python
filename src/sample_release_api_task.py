from digitalai.release.integration import BaseTask


class SetSystemMessage(BaseTask):
    """
        Sets the system message using the Release API client.

        Preconditions:
            - The 'Run as user' property must be set on the release.
            - The executing user must have valid credentials.
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
