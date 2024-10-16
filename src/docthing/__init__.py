# SPDX-License-Identifier: MIT
''' BEGIN FILE DOCUMENTATION (level: 1)
Here it is a simple TypeScript project structure with a minimal setup
as an example:

## Project Structure

```
project-root/
 ├── docthing.jsonc
 ├── docthing.conf
 ├── INTRO.md
 ├── README.md
 └── src/
      ├── main.ts
      └── utils.ts
```

### docthing.jsonc

```json
{
    "main-title": "example-project",
    "quick": "README.md",
    "intro": "INTRO.md",
    "usage": {
        "main": "src/main.ts",
        "utils": "src/utils.ts"
    }
}
```

### docthing.conf

```ini
[main]
index_file=docthing.jsonc
meta=nav.md

[output]
dir={index-file-dir}/documentation
type=markdown

[parser]
begin_doc=BEGIN FILE DOCUMENTATION
end_doc=END FILE DOCUMENTATION
doc_level=1
extensions=js,ts
iexts=test.{extensions}
allow_sl_comments=false
peek_lines=1

[parser|js|ts]
begin_ml_comment=/*
end_ml_comment=*/
sl_comment=//
allow_sl_comments=false
```

### src/*.ts

File `src/main.ts`:
```ts
/* BEGIN FILE DOCUMENTATION (level: 1)
This is a TypeScript file with an heading documentation.
This text will be outputed as documentation in the file
`./documentation/markdown/usage/main.md`.
END FILE DOCUMENTATION */
```

File `src/util.ts`:
```ts
/* BEGIN FILE DOCUMENTATION (level: 2)
This text will be outputed as documentation in the file
`./documentation/markdown/usage/util.md`.
END FILE DOCUMENTATION */
```

Note that the `level` attribute is optional and defaults to 1.
In the second file, `util.ts`, the `level` attribute is set to 2;
this means that it will be included in the documentation only
if the `doc_level` attribute in the configuration file is set to 2
or higher.
END FILE DOCUMENTATION '''

from .documentation_content import Document, ResourceReference
from .documentation_blob import DocumentationBlob, DocumentationNode
from .plugins.exporter_interface import Exporter
from .plugins.meta_interpreter_interface import MetaInterpreter

__all__ = [
    "Document",
    "ResourceReference",
    "DocumentationBlob",
    "DocumentationNode",
    "Exporter",
    "MetaInterpreter"
]
