
from docthing.documentation_content import ResourceReference
from ..meta_interpreter_interface import MetaInterpreter, InterpretedCode


class NAVInterpreter(MetaInterpreter):
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
            res.append('<div class="nav-buttons">')

        if prev is not None:
            return res.append(NAVReference(prev))

        if prev is not None and next is not None:
            res.append('')

        if next is not None:
            return res.append(NAVReference(next))

        if prev is not None or next is not None:
            res.append('</div>')

        return res

class NAVReference(ResourceReference):
    '''
    A class that represents a reference to a PlantUML diagram.
    '''

    def __init__(self, leaf):
        super().__init__(None, 'import-file', use_hash=leaf.get_title())

    def get_ext(self):
        return 'md'

    def compile(self) -> str | bytes:
        return None
