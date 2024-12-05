# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 2)
`MetaInterpreter` is an abstract class that defines the interface for
meta-interpreters plugins.

> Even if you are interested in developing a meta-interpreter,
> I suggest you to read the documentation of [`Exporter`](@Exporter)
> plugins too to have a better understanding of how the whole
> process works.

This kind of plugins are used to modify the documentation blob by
intervening at the beginning of the file, at the end of the file or
at the beginning of each _special block_ of the file.

## Beginning and ending of file modes

When a meta-interpreter is used in `begin_file` or `end_file` mode,
it will be called once for each [`Document`](@Document) in the
documentation blob to apply some changes to it at the beginning
or at the end of the file respectively. A good example of this is
the `nav.md` meta-interpreter that is used to generate the navigation
links at the end of the page (`end_file` mode).

## Block mode

When a meta-interpreter is used in `block` mode, it will be look for
a special line to start _capturing_ the content of the block until
it finds a special line to stop capturing it. These special lines
are defined by the user by implementing the `_get_begin_code` and
`_get_end_code` methods. These methods should return a string or a
regualr expression since they will be passed as argument in `re.search`
used in `is_begin_code` and `is_end_code` methods respectively.
Finally, once the block is captured, the `generate_resource` method
will be called to generate a resource that will be added to the
`Document` replacing the block with a reference to the resource
in the form of a [`ResourceReference`](@ResourceReference). This kind
of objects are later used by the [`Exporter`](@Exporter) plugin to
generate the output file and the way it is built should be defined in the
implementation of the method `generate_resource`. A good example of this
is the builtin `plantuml` plugin that will look for `@startuml` and
`@enduml` to capture the PlantUML code blocks and replace them with an
implementation of `ResourceReference` called `PlantUMLReference`.

As you might have guessed at this point, when you create a `MetaInterpreter`
plugin, you should implement also a custom `ResourceReference` that will be
used by `Exporter` plugins to generate the output file. In order ti do so
the exporter will need to know if the resource need to be compiled (and
enevtually how to do it) and what the output extension will be. The compilation
process should be defined in the `compile` method of the `ResourceReference`
implementation and the output extension should be defined in the `get_ext`
method. The extension is later used by the exporter to determine the exact
output file name.

END FILE DOCUMENTATION '''

import re

from abc import abstractmethod

from .plugin_interface import PluginInterface


class MetaInterpreter(PluginInterface):
    '''
    MetaInterpreter is an abstract class that defines the interface for meta-interpreters.
    '''

    def __init__(self, mode='block'):
        '''
        Initializes the MetaInterpreter instance.
        '''
        if mode not in ['block', 'begin_file', 'end_file']:
            raise ValueError(
                f'Mode {mode} is not supported. ' +
                'Please use either \'block\', \'begin_file\' or \'end_file\'.')

        super().__init__()
        self.mode = mode

    def _enable(self):
        '''
        Loads the MetaInterpreter instance by checking if the dependencies are available.
        '''
        if not self.are_dependencies_available():
            raise ValueError('Dependencies for the ' +
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
