# pip-split-requirements

[![PyPI - Version](https://img.shields.io/pypi/v/pip-split-requirements.svg)](https://pypi.org/project/pip-split-requirements)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pip-split-requirements.svg)](https://pypi.org/project/pip-split-requirements)

-----

Split a pip requirement files according to regular expression patterns rules.

**Table of Contents**

- [pip-split-requirements](#pip-split-requirements)
  - [Installation](#installation)
  - [Quick start](#quick-start)
  - [CLI Usage](#cli-usage)
  - [Configuration in pyproject.toml](#configuration-in-pyprojecttoml)
  - [Usage as a pre-commit hook](#usage-as-a-pre-commit-hook)
  - [License](#license)

## Installation

```console
pipx install pip-split-requirements
```

## Quick start

Assume the following `requirements.txt`:

```text
--find-links wheelhouse
pkga
git+https://github.com/some/project
pkgb
```

Running

```console
pip-split-requirements -g slow:git requirements.txt
```

Will create `requirementsgroup-slow.txt`:

```text
--find-links wheelhouse
git+https://github.com/some/project
```

and `requirementsgroup-other.txt`:

```text
--find-links wheelhouse
pkga
pkgb
```

## CLI Usage

```text
Usage: pip-split-requirements [OPTIONS] REQUIREMENTS_FILE...

  Split a pip requirements file into multiple files according to patterns.

  Patterns are regular expressions against which requirement lines are
  searched to determine if they belong to a group. Group specs are evaluated
  in order, and the first match determines in which group the line goes.

  Comment lines are ignored.

  Option lines are emitted in all groups.

Arguments:
  REQUIREMENTS_FILE...  The requirements files to split. If not specified,
                        they are read from pyproject.toml.

Options:
  -g, --group-spec TEXT           Group specifications in form name:pattern.
  -p, --prefix TEXT               Each requirements group file will be named
                                  {prefix}-{group_name}.txt. The prefix can
                                  contain path separators, to generate files
                                  into a chosen directory.  [default:
                                  requirementsgroup]
  --default-group / --no-default-group
                                  Automatically append a group named 'other',
                                  matching all lines not matched by other
                                  groups.  [default: default-group]
  --remove-empty / --no-remove-empty
                                  Remove empty requirements group files.
                                  [default: no-remove-empty]
  -r, --project-root DIRECTORY    The project root directory. The generated
                                  requirements files will be relative to this
                                  directory. Default options and arguments are
                                  read from pyproject.toml in this directory.
                                  [default: .]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
```

## Configuration in pyproject.toml

`pip-split-requirements` can be configured using `pyproject.toml`. The following values are read from the `tool.pip-split_requirements` section:

- group_specs: list of strings
- prefix: string
- default_group: boolean
- remove_empty: boolean
- requirements_files: list of strings

Command line options and argument have precedence over `pyproject.toml` values.

The following example configuration split `requirements.txt` and `requirements-test.txt`
into a group named `vcs` with requirements containing the word `git+https` or `git+ssh`
and another group with everything else, as `build/reqgroup-*.txt`.

```toml
[tool.pip-split-requirements]
prefix = "build/reqgroup"
group_specs = ["vcs:git.(https|ssh)"]
requirements_files = ["requirements.txt", "requirements-test.txt"]
```

## Usage as a pre-commit hook

The following section of `.pre-commit-config.yaml` will run `pip-split-requirements`
according using the configuration in `pyproject.toml`. This pre-commit hook runs when
either `pyproject.toml`, `.pre-commit-config.yaml`, or any file matching the pattern
`.*requirement.*\.txt` change.

```yaml
  - repo: https://github.com/sbidoul/pip-split-requirements
    rev: v0.7.0
    hooks:
      - id: pip-split-requirements
```

## License

`pip-split-requirements` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.
