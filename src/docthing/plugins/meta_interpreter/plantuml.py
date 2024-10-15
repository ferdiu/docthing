# SPDX-License-Identifier: MIT

import subprocess as sp
from typing import Union

from ...documentation_content import ResourceReference
from ..meta_interpreter_interface import MetaInterpreter


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

    def _should_keep_beginning(self):
        return True

    def _should_keep_ending(self):
        return True

    def generate_resource(self, source):
        return PlantUMLReference(source)


class PlantUMLReference(ResourceReference):
    '''
    A class that represents a reference to a PlantUML diagram.
    '''

    def __init__(self, source):
        super().__init__(source, 'image')

    def get_ext(self):
        return 'png'

    def compile(self) -> Union[bytes, str]:
        try:
            completed_process = sp.run(
                ['plantuml', '-tpng', '-pipe'],
                input=''.join(self.source).encode('utf-8'),
                stdout=sp.PIPE,
                check=True,
            )
            return completed_process.stdout
        except sp.CalledProcessError as e:
            raise Exception(f'Error while compiling PlantUML code: {e.stderr}')
