# `docthing` Configuration File Documentation

The configuration file allows you to control various aspects of how docthing processes your source code, including parsing rules, output formats, and file extensions to target.

## Table of Contents

- [Overview](#overview)
- [Predefined Variables](#predefined-variables)
- [Sections](#sections)
- [Variables](#variables)
- [Example](#example-configuration-file)

## Overview

By default the configuration file is assumed to be named `docthing.conf` and is located in the same directory as the `index-file`.

The configuration file follows a standard format that supports the use of variables and predefined values. Variables can be referenced using curly braces (`{}`), and sections are denoted with square brackets (`[]`). Variables must be defined before being used in the configuration file, and the file is divided into sections with specific purposes. Some settings can be overridden via command-line options.

## Predefined Variables

- `index-file-dir`: Represents the directory where the index file is located. It is often used in output paths to avoid hardcoding directory structures.

## Sections

### `[main]`

The `main` section includes general configurations, such as file extensions to process and ignored files.

- `index_file`: Specifies the name of the index file. If this is also provided via the command line, the command-line option takes precedence.
> Example:
> `index_file=index.jsonc`

- `exts`: Specifies the file extensions that docthing should process. If directories are provided in the index file, this list will be used to find files to include in the documentation. Multiple extensions can be provided, separated by commas.
> Example:
> `extensions=js,jsx,ts,tsx`

- `iexts`: Specifies file extensions to ignore when generating documentation. You can reference previously declared variables here, such as {extensions}.
> Example:
> `iexts=test.{extensions}`

- `meta`: Indicates the additional metadata to detect within the files. Markdown is always detected, but you can specify others like plantuml for diagram inclusion.
> Example:
> `meta=plantuml`

### `[output]`

This section configures the output of the documentation process, such as the output directory and format.

- `dir`: Specifies the directory where the documentation will be generated. You can use predefined variables like {index-file-dir} to dynamically set the directory based on the index file's location.
> Example:
> `dir={index-file-dir}/documentation`

- `type`: Specifies the formats in which documentation should be generated. Available options include latex, html, markdown, and pdf. Please, note that the pdf generation requires the LaTeX source to be generated.
> Example:
> `type=latex,html,markdown,pdf`

### `[parser]`

The parser section controls how docthing parses the source code for documentation. It defines patterns to detect the start and end of documentation blocks, as well as some additional options for controlling the parsing process.

- `begin_doc`: A string that defines what the parser should look for to detect the start of a documentation block.
> Example:
> `begin_doc=BEGIN FILE DOCUMENTATION`

- `end_doc`: A string that defines what the parser should look for to detect the end of a documentation block.
> Example:
> `end_doc=END FILE DOCUMENTATION`

- `doc_level`: Defines the maximum documentation level to extract. A level of 0 indicates no limit. Refer to docthing's documentation for further details.
> Example:
> `doc_level=1`

- `allow_sl_comments`: This boolean value specifies whether single-line comments are allowed for documentation. By default, only multi-line comments are used.
> Example:
> `allow_sl_comments=false`

- `peek_lines`: Controls how many lines should be peeked ahead when searching for documentation within a file. Setting this to 0 means all lines will be scanned, though this is not recommended for performance reasons.
> Example:
> `peek_lines=1`

### `[parser|extsions-list]`

This section provides language-specific parser configurations for specific languages source-code files. These settings can override general parser settings for these specific file types.

- `begin_ml_comment`: Specifies the string used to mark the start of multi-line comments in JavaScript/TypeScript files.
> Example:
> `begin_ml_comment=/**`

- `end_ml_comment`: Specifies the string used to mark the end of multi-line comments in JavaScript/TypeScript files.
> Example:
> `end_ml_comment=*/`

## Variables

Variables are represented by names enclosed in curly braces (`{}`). They can be used to replace specific values within the configuration. For instance, the variable `{index-file-dir}` refers to the directory of the index file.

Variables can be referenced within the same section or across sections. When referencing variables from the same section, only the variable name is required (e.g., `{var}`). To reference variables from other sections, prefix them with the section name (e.g., `{section.var}`).

## Example Configuration File

```conf
[main]
index_file=index.jsonc
extensions=js,jsx,ts,tsx
iexts=test.{extensions}
meta=plantuml

[output]
dir={index-file-dir}/documentation
type=latex,html,markdown,pdf

[parser]
begin_doc=BEGIN FILE DOCUMENTATION
end_doc=END FILE DOCUMENTATION
doc_level=1
allow_sl_comments=false
peek_lines=1

[parser|js|jsx|ts|tsx]
begin_ml_comment=/**
end_ml_comment=*/
allow_sl_comments=false
```
### In this example:

The index file is `index.jsonc`.
Only `js`, `jsx`, `ts`, and `tsx` files will be processed.
Files with the pattern `test.{extensions}` will be ignored.
The output will be generated in a documentation folder inside the index file's directory.
Documentation will be output in LaTeX, HTML, Markdown, and PDF formats.
Parsing is customized for JavaScript and TypeScript files with multi-line comment support and no single-line comments.

This configuration ensures `docthing` processes the right files, generates documentation in multiple formats, and parses documentation blocks correctly.