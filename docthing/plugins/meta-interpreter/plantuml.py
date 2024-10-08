
from ..meta_interpreter import MetaInterpreter


class PlantUMLInterpreter(MetaInterpreter):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
