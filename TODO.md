
# TODOs

- config:
    - [X] make use of `main.extensions` and `main.iexts` variables
    - [X] load only named plugins in `main.meta` variable
    - [X] load only named plugins in `output.type` variable
    - [ ] allow `[meta|<meta-name>]` section in config file
    - [ ] allow `[type|<type-name>]` section in config file
- doc-parser:
    - [ ] allow the use of `parser.allow_sl_comments`
    - [X] properly handle all cases when reading the `index_file`
- general:
    - [X] build `DocumentationBlob` instead of dumping `.md` files in the output directory
    - [ ] use `options` inside `DocumentationBlob` when exporting using an `Exporter`
- refactor:
    - [ ] `extensions` and `iexts` should be moved into `parser` section

### General ideas not implemented nor really designed

- All plugins, both exporter and meta-interpreters, should be able to handle the tree-like structure of `DocumentationBlob`
