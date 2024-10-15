# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 2)

TODO: meta_interpreter_interface documentation

This comes from the `docthing/plugins/meta_interpreter.py` file.

@startuml
Bob -> Alice : hello
@enduml

In the documentation, the code block should have been replaced by a uuid.

END FILE DOCUMENTATION '''

import re

from abc import abstractmethod

from .plugin_interface import PluginInterface


class MetaInterpreter(PluginInterface):
    '''
    MetaInterpreter is an abstract class that defines the interface for meta-interpreters.
    '''

    def __init__(self, config, mode='block'):
        '''
        Initializes the MetaInterpreter instance with the provided configuration.
        '''
        if mode not in ['block', 'begin_file', 'end_file']:
            raise Exception(
                f'Mode {mode} is not supported. ' +
                'Please use either \'block\', \'begin_file\' or \'end_file\'.')

        super().__init__(config)
        self.config = config
        self.mode = mode

    def _enable(self):
        '''
        Loads the MetaInterpreter instance by checking if the dependencies are available.
        '''
        if not self.are_dependencies_available():
            raise Exception('Dependencies for the ' +
                            f'{self.get_name()} interpreter are not available.')

    def _disable(self):
        '''
        Unloads the MetaInterpreter instance.
        '''
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

    @abstractmethod
    def generate_resource(self, source):
        '''
        Generate a resource reference from the given source.
        '''
        pass

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

    def find_first_begin_code_index(self, lines):
        '''
        Find the index of the first line in the list that is the beginning of a code block.
        '''
        return next((i for i, line in enumerate(lines)
                    if self.is_begin_code(line)), None)

    def find_first_end_code_index(self, lines, beginning=0):
        '''
        Find the index of the first line in the list that is the ending of a code block
        from the `beginning` line of the code block.
        '''
        return next((i for i, line in enumerate(lines[beginning:])
                    if self.is_end_code(line)), None) + beginning

    def find_begin_and_end(self, lines):
        '''
        Find the first and last line of the code block in the given list of lines.
        '''
        first_line = self.find_first_begin_code_index(lines)

        if first_line is None:
            return None, None

        last_line = self.find_first_end_code_index(lines, first_line)

        return first_line, last_line

    def interpret_leaf_begin_file(self, leaf):
        '''
        Interpret the leaf prepending a resource at the beginning of it.
        '''
        leaf.get_content().prepend_resource(
            self.generate_resource(leaf))

    def interpret_leaf_end_file(self, leaf):
        '''
        Interpret the leaf appending a resource to the end of it.
        '''
        leaf.get_content().append_resource(
            self.generate_resource(leaf))

    def interpret_leaf_block(self, leaf):
        '''
        Interpret the leaf search for a block of code and return the result.
        '''
        first_line, last_line = self.find_begin_and_end(leaf.get_content())

        if first_line is None:
            return

        if last_line is None:
            print('Warning: reached end of file without finding end of ' +
                  f'code ({self.get_name()}): giving up')

        if not self._should_keep_beginning():
            content_first_line = first_line + 1
        else:
            content_first_line = first_line

        if not self._should_keep_ending():
            content_last_line = last_line
        else:
            content_last_line = last_line + 1

        leaf.get_content().replace_lines_with_reference(
            self.generate_resource(
                leaf.get_content()[
                    content_first_line,
                    content_last_line]),
            first_line,
            last_line)

    def interpret_leaf(self, leaf):
        '''
        Interpret the leaf and return the result.
        '''
        if self.mode == 'begin_file':
            self.interpret_leaf_begin_file(leaf)
        elif self.mode == 'end_file':
            self.interpret_leaf_end_file(leaf)
        elif self.mode == 'block':
            self.interpret_leaf_block(leaf)

    def interpret(self, documentation_blob):
        '''
        Search all leaf in DocumentationBlob and interpret the code blocks.

        This will replace lines in `Document`s with the result of the interpretation
        which is a `ResourceReference` implementation.
        '''
        for leaf in documentation_blob.get_leaves():
            if leaf.is_lazy():
                leaf.unlazy()

            self.interpret_leaf(leaf)
