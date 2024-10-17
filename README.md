# 📑 docthing

> Someone once said: _"The software is not such if not documented."_ I do not really remember who but I strongly agree with her/him.

Simple tool to extract high-level documentation from the projects.

### Rationale

Documentation is crucial for maintaining a clear understanding of a project's architecture, ensuring that developers and stakeholders can easily comprehend how the system works. Keeping documentation up-to-date with the source code is vital to avoid discrepancies that can lead to confusion and inefficiency. To achieve this, it's essential to keep documentation as close to the code as possible, enabling seamless updates as the code evolves. Additionally, offering multiple levels of documentation, as highlighted by the [C4](https://c4model.com/) model, allows different audiences—whether technical experts or non-technical stakeholders—to access the right level of detail, from high-level system overviews to detailed component interactions.

### Features

- 🔧 Highly configurable
- 📈 Scalable
- 🏴‍☠️ Language agnostic
- 🤏 Small fingerprint
- 🔌 Extensible (Plugins)
- 🖼️ LOD (Level Of Details: choose the in-depth level of your documentation dynamically)

## Table of Contents

- [Usage](#usage)
- [Index File](#index-file)
- [Config file](#config-file)

## Usage

```bash
docthing \
    <index-file|project-directory> \
    [--config=<config-file>] \
    [--config-dump] \
    [--outdir=<output-directory>]
```

where:
- `index-file` is file in the root of the directory containing the project you want to create documentation for (see [`Index File section`](#index-file)); alternatively this can be the name of the project root which will have to contain a file named `docthing.jsonc` which will be used as the `index-file`;
- `config-file` is the path, relative to the directory containing the `project-index-file`, of the configuration file to use for docthing (see [`Config File section`](#config-file)) [default: `./docthing.conf`];
- `config-dump` is a flag to print to stdout the default configuration file used by docthing;
- `output-directory` is the absolute path to the directory where the documentation output will be produced [default: `./documentation` relative to the directory containing the `index-file`]; if destination does not exsist it will be created.

## Index File

The index file is a JSON (eventually with comments) with following structure:

```JSONC
{
    "intro": "<optional path to the introduction file>",
    "quick": "<optional path to the quick start documentation file>",
    "chapter_name": {
        "section_name": "file or directory containing documentation to print",
        [...],
        "section_name": {
            "subsection_name": {...},
            "subsection_name": "file or directory containing documentation",
            [...],
            "subsection_name": [
                "filename 1",
                "filename 2",
                "filename 3"
            ]
        },
        [...]
    },
    "another_section_name": {...},
    [...]
}
```

Basically the documentation will be splitted into `chapters` declared by the outmost `keys` in the JSON file. If an `intro` key is specified it should be valued with the path to a markdown formatted file containing a brief description of the project. If a `quick` key is specified it will be used to create a small chapter containing a _Quick Start_ guide for the project and should be valorized with the path pointing to a markdown formatted file containing these instructions (it could be aggo idea to use the `README.md` file of your project).

> **PATHS**: all paths specified in the `index-file` should be relative to the file it-self!

The value of each chapter has to be a _Documentation Piece_ which is one of the following:

- a `string` containing the path to a source-code file containing the documentation to print;
- a `vector` containing the paths to source-code files containing the documentation to print or a _Documentation Piece_;
- a `dict` in the form of a _Documentation Piece_ as value and a `string` as key.

Each _Documentation Piece_ has the same form as a chapter with the exception that the `intro` and `quick` keys are not allowed (actually they are allowed but have no special meaning) and have another special key called `__index__` which is a `string` containing the path to another `index-file` nested in the project. This is useful to create nested documentation for a project and is encouraged way of structuring the documentation to make it more flexible.

In general the `verctor` inside a _Documentation Piece_ is discouraged since normally the `key`s of the `dict` are used to create the title of a _section_ or _subsection_ and this will not be the case if the `vector` is used.

## Config File

By default the configuration file is assumed to be named `docthing.conf` and is located in the same directory as the `index-file`.

The configuration file follows a standard format that supports the use of variables and predefined values. Variables can be referenced using curly braces (`{}`), and sections are denoted with square brackets (`[]`). Variables must be defined before being used in the configuration file, and the file is divided into sections with specific purposes. Some settings can be overridden via command-line options.

For more information on the configuration file format, please refer to the [documentation](./CONFIG-FILE.md).

## Documentation options

The _documentations options_ are optional annotations that can be added at the right of the beginning of the documentation section. Newlines are not allowed.

> Example:
> ```conf
> /* BEGIN FILE DOCUMENTATION (level: 2, user-defined-option: "value")
> [markdown-formatted documentation goes here]
> END FILE DOCUMENTATION */
> ```

The options can be customized by the user but are not mandatory. Some options are provided by default and are described in the next section.

### Provided options

- `level: (number)`: the level of the documentation section. This is a number indicating how in-depth the documentation is. If not specified it will be set to 0 by default. This option is used to choose whether or not to include documentation in the final output based on the selected `documentation-level` configured in the configuration file or passed via command-line options: it works as an upper bound threshold;
> Example: the following documentation will be included in the final output only if the `documentation-level` is set to 2 or higher:
> ```conf
> /* BEGIN FILE DOCUMENTATION (level: 2)
> [markdown-formatted documentation goes here]
> END FILE DOCUMENTATION */
> ```

- `level-only: (boolean)`: if set to `true` the documentation will be included in the final output only if the `documentation-level` configured in the configuration file or passed via command-line options is equal to the `level` option. Has no effect if not associated with a `level` option;
> Example: the following documentation will be included in the final output only if the `documentation-level` is set **exactly** to 2:
> ```conf
> /* BEGIN FILE DOCUMENTATION (level: 2, level-only: true)
> [markdown-formatted documentation goes here]
> END FILE DOCUMENTATION */
> ```

## Contributing

If you'd like to contribute to the project, please follow these steps:

- Fork the repository.
- Create a new branch for your changes.
- Make your changes and commit them.
- Push your changes to your fork.
- Create a pull request to the main repository.

## License

See the [LICENSE](./LICENSE) file for details.
