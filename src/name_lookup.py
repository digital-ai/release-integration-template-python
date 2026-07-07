from digitalai.release.integration import BaseTask


LOOKUP_NAMES = ("Alice", "Benjamin", "Charlotte", "Daniel", "Emma")


class NameLookup(BaseTask):
    """
         Lookup a name from a predefined list
    """

    def execute(self) -> None:
        result = [{"label": name, "value": name} for name in LOOKUP_NAMES]
        self.set_output_property("commandResponse", result)
