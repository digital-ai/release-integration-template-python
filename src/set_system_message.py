from digitalai.release.integration import BaseTask
from digitalai.release.v1.api.configuration_api import ConfigurationApi
from digitalai.release.v1.model.system_message_settings import SystemMessageSettings


class SetSystemMessage(BaseTask):
    """
        Sets the system message in the Release UI by invoking the API.
    """
    def execute(self) -> None:
        configuration_api = ConfigurationApi(self.get_default_api_client())

        system_message = SystemMessageSettings(
            type='xlrelease.SystemMessageSettings',
            id='Configuration/settings/SystemMessageSettings',
            message=self.input_properties['message'],
            enabled=True,
            automated=False
        )

        configuration_api.update_system_message(system_message_settings=system_message)

        self.add_comment(f"System message updated to \"{self.input_properties['message']}\"")

