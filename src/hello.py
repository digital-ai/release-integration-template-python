from digitalai.release.integration import BaseTask


class Hello(BaseTask):
    """
       Creates a greeting based on a name
    """
    def execute(self) -> None:

        # Get input properties
        name = self.input_properties['yourName']
        if not name:
            raise ValueError("The 'yourName' field cannot be empty")

        greeting = f"Hello {name}"

        # Add to the comment section of the task in the UI
        self.add_comment(greeting)

        self.set_output_property('greeting', greeting)

