''' BEGIN FILE DOCUMENTATION (level: 1)

This comes from the `docthing/plugins/meta_interpreter.py` file.

@startuml
Bob -> Alice : hello
@enduml

In the documentation, the code block should have been replaced by a uuid.

END FILE DOCUMENTATION '''

import os
import re
import uuid

from abc import ABC, abstractmethod
from .plugin_interface import PluginInterface


class MetaInterpreter(PluginInterface):
    """
    MetaInterpreter is an abstract class that defines the interface for meta-interpreters.
    """

    def __init__(self, config):
        """
        Initializes the MetaInterpreter instance with the provided configuration.

        Args:
            config (dict): The configuration for the MetaInterpreter instance.
        """
        super().__init__(config)
        self.config = config

    def _load(self):
        """
        Loads the MetaInterpreter instance by checking if the dependencies are available.
        """
        if not self.are_dependencies_available():
            raise Exception(
                f'Dependencies for the {
                    self.get_name()} interpreter are not available.')

    def _unload(self):
        """
        Unloads the MetaInterpreter instance.
        """
        pass

    @abstractmethod
    def _get_begin_code(self):
        '''
        Return the regular expression for the beginning of the code block.
        '''
        pass

    @abstractmethod
    def _get_end_code(self):
        '''
        Return the regular expression for the end of the code block.
        '''
        pass

    def _should_keep_beginning(self):
        '''
        Return whether the beginning of the code block should be kept in the final code or not.
        '''
        return False

    def _should_keep_ending(self):
        '''
        Return whether the end of the code block should be kept in the final code or not.
        '''
        return False

    def is_begin_code(self, line):
        '''
        Return whether the given line is the beginning of the code block.
        '''
        return re.search(self._get_begin_code(), line) is not None

    def is_end_code(self, line):
        '''
        Return whether the given line is the end of the code block.
        '''
        return re.search(self._get_end_code(), line) is not None

    def extract_code(self, lines, beginning=0):
        '''
        Extract the code block from the given lines starting from line number `beginning`
        (indexed from 0).
        '''
        res = []

        if self._should_keep_beginning():
            real_beginning = beginning
        else:
            real_beginning = beginning + 1

        for i in range(real_beginning, len(lines)):
            # reached end of plantuml code
            if self.is_end_code(lines[i]):
                if self._should_keep_ending():
                    res.append(lines[i])
                break

            # reached end of file without finding end of code
            if i == len(lines) - 1:
                print(
                    f'Warning: reached end of file without finding end of code ({
                        self.get_name()}): giving up')
                res = []
                break

            res.append(lines[i])

        return res

    def interpret(self, lines, beginning=0):
        '''
        Interpret the code block starting from line number `beginning` (indexed from 0).
        '''
        code = self.extract_code(lines, beginning)
        return InterpretedCode(code, self.config['output_dir'])


class InterpretedCode(ABC):
    '''
    Represents an interpreted code block that can be compiled and output to a file.

    The `InterpretedCode` class is an abstract base class that provides a common interface
    for interpreting and compiling code blocks. Subclasses of `InterpretedCode` must implement
    the `_command` and `_get_output_exntesion` methods to define how the code block is
    interpreted and compiled.

    The `InterpretedCode` class has the following attributes:
    - `uuid`: A unique identifier for the interpreted code block.
    - `code_lines`: A list of strings representing the lines of code to be interpreted.
    - `output_dir`: The directory where the compiled output will be written.

    The `compile` method writes the compiled output to a file in the `output_dir` directory,
    with the filename based on the `uuid` and the output file extension.

    The `get_compiled_path` method returns the full path to the compiled output file.
    '''

    def __init__(self, code_lines, output_dir):
        '''
        Initializes an `InterpretedCode` object with the provided code lines and output
        directory.

        Args:
            code_lines (list[str]): The lines of code to be interpreted.
            output_dir (str): The directory where the interpreted code will be output.
        '''
        self.uuid = str(uuid.uuid4())
        self.code_lines = code_lines
        self.output_dir = output_dir

    @abstractmethod
    def _command(self, output_file):
        '''
        Executes the command to interpret the code block and write the output to the given
        output_file.
        '''
        pass

    @abstractmethod
    def _get_output_exntesion(self):
        '''
        Returns the file extension of the output file.
        '''
        pass

    def compile(self):
        '''
        Compiles the interpreted code block and writes the output to a file in the output
        directory.
        '''
        with open(self.uuid + '.' + self._get_output_exntesion(), 'w') as f:
            self._command(f)

    def get_compiled_path(self):
        '''
        Returns the full path to the compiled output file.
        '''
        return os.path.join(
            self.output_dir,
            self.uuid +
            '.' +
            self._get_output_exntesion())
