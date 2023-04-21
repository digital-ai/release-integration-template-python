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
