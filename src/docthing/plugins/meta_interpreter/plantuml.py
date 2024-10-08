
import subprocess as sp

from ..meta_interpreter_interface import MetaInterpreter, InterpretedCode


class PlantUMLInterpreter(MetaInterpreter):
    '''
    A meta-interpreter for interpreting PlantUML code blocks.
    '''
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def get_name(self):
        return 'plantuml'

    def get_description(self):
        return 'PlantUML meta-interpreter for docthing'

    def get_dependencies(self):
        return ['plantuml']

    def _get_begin_code(self):
        return r'^@startuml$'

    def _get_end_code(self):
        return r'^@enduml$'

    def _does_keep_beginning(self):
        return True

    def _does_keep_ending(self):
        return True


class InterpretedPlantUML(InterpretedCode):
    '''
    Represents an interpreted PlantUML diagram.

    The `InterpretedPlantUML` class is responsible for rendering a PlantUML diagram from a set of code lines. It uses the `plantuml` command-line tool to generate a PNG image from the PlantUML code.

    The `_command` method runs the `plantuml` command with the necessary arguments to generate the PNG output from the PlantUML code lines. The `_get_output_exntesion` method returns the file extension of the generated output, which is 'png' in this case.
    '''
    def __init__(self, code_lines):
        super().__init__(code_lines)

    def _command(self, output_file):
        sp.run(['plantuml', '-tpng', '-pipe'],
               stdin='\n'.join(self.code_lines),
               stdout=output_file)

    def _get_output_exntesion(self):
        return 'png'
