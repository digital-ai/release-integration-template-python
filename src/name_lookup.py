from digitalai.release.integration import BaseTask


class NameLookup(BaseTask):
    """
         Lookup a name from a predefined list
    """
    def execute(self) -> None:

        # Get the typed value from the input
        # name = self.input_properties["_ci"]['yourName']

        result = [
            {'label': 'Alice', 'value': 'Alice'},
            {'label': 'Benjamin', 'value': 'Benjamin'},
            {'label': 'Charlotte', 'value': 'Charlotte'},
            {'label': 'Daniel', 'value': 'Daniel'},
            {'label': 'Emma', 'value': 'Emma'}
        ]
        self.set_output_property("commandResponse", result)
