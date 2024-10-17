# SPDX-License-Identifier: MIT

import os
from typing import Union

from ...documentation_content import ResourceReference
from ..meta_interpreter_interface import MetaInterpreter


class MarkdownNAVInterpreter(MetaInterpreter):
    '''
    A meta-interpreter for interpreting PlantUML code blocks.
    '''

    def __init__(self, config):
        super().__init__(config, 'end_file')
        self.config = config

    def get_name(self):
        return 'nav.md'

    def get_description(self):
        return 'Create navigation buttons in each documentation page'

    def get_dependencies(self):
        return []

    def _get_begin_code(self):
        return r'^@startdoclink$'

    def _get_end_code(self):
        return r'^@startdoclink$'

    def _should_keep_beginning(self):
        return True

    def _should_keep_ending(self):
        return True

    def generate_resource(self, source):
        leaf = source
        prev = leaf.get_previous_tree_leaf_breadth_first()
        next = leaf.get_next_tree_leaf_breadth_first()

        res = []

        if prev is not None or next is not None:
            res.append(
                '<div class="nav-buttons" style="text-align: center; width: 100%; ' +
                'border-radius: .5rem; border: 1px solid; padding: 1rem; ' +
                'margin-bottom: 1rem; display: flex; justify-content: space-between">')

        if prev is not None:
            p = leaf.get_path_to(prev)
            p = os.path.join(
                *[n if isinstance(n, str) else n.get_title() for n in p])
            res.append(MarkdownNAVReference(p))
        elif next is not None:
            res.append(
                '<span></span>\n')

        if prev is not None and next is not None:
            res.append(
                '<span style="margin-left: 1rem; margin-right: 1rem">-</span>\n')

        if next is not None:
            p = leaf.get_path_to(next)
            p = os.path.join(
                *[n if isinstance(n, str) else n.get_title() for n in p])
            res.append(MarkdownNAVReference(p))

        if prev is not None or next is not None:
            res.append('</div>')

        return res


class MarkdownNAVReference(ResourceReference):
    '''
    A class that represents a reference to another `markdown` file.
    '''

    def __init__(self, path_to_file):
        super().__init__(None, 'import-file', use_hash=path_to_file)

    def get_ext(self):
        return 'md'

    def compile(self) -> Union[bytes, str]:
        return None
