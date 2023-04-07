from digitalai.release.integration import BaseTask


class Hello(BaseTask):
    """
       Creates a greeting based on a name
    """

    def execute(self) -> None:

        # Get the name from the input
        name = self.input_properties['yourName']
        if not name:
            raise ValueError("The 'yourName' field cannot be empty")

        # Create greeting
        greeting = f"Hello {name}"

        # Add greeting to the task's comment section in the UI
        self.add_comment(greeting)

        # Put greeting in the output of the task
        self.set_output_property('greeting', greeting)

