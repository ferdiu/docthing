
# TODOs

- config:
    - [X] make use of `main.extensions` and `main.iexts` variables
    - [X] load only named plugins in `main.meta` variable
    - [X] load only named plugins in `output.type` variable
    - [ ] allow `[meta|<meta-name>]` section in config file
    - [ ] allow `[type|<type-name>]` section in config file
    - [X] create a command line option to dump a basic config file
- doc-parser:
    - [X] allow the use of `parser.allow_sl_comments`
    - [X] properly handle all cases when reading the `index_file`
- general:
    - [X] build `DocumentationBlob` instead of dumping `.md` files in the output directory
    - [X] use `options` inside `DocumentationBlob` when exporting using an `Exporter`
- refactor:
    - [X] `extensions` and `iexts` should be moved into `parser` section
- documentation:
    - [ ] finish documentation
- CI/CD:
    - [ ] add a possibility to use it as a pre-commit step checking if all files changed form previous commit changed their documentation too (with optional possibility to exit non-zero is so)
    - [ ] add github action to upload documentation to github wiki
    - [ ] add gitlab CI to upload documentation to gitlab wiki

### General ideas not implemented nor really designed

- All plugins, both exporter and meta-interpreters, should be able to handle the tree-like structure of `DocumentationBlob`
