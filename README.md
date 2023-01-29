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

  Comment lines are ignored. Option lines are emitted in all groups.

Arguments:
  REQUIREMENTS_FILE...  [required]

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
  --help                          Show this message and exit.
```

## Usage as a pre-commit hook

The following section of `.pre-commit-config.yaml` will split `requirements.txt` into a
group named `vcs` with requirements containing the word `git` and another group with
everything else, as `build/reqgroup-*.txt`.

```yaml
  - repo: https://github.com/sbidoul/pip-split-requirements
    rev: v0.1.0
    hooks:
      - id: pip-split-requirements
        files: ^requirements\.txt$
        args:
          - --prefix=build/reqgroup
          - --group-spec=vcs:git
```

## License

`pip-split-requirements` is distributed under the terms of the
[MIT](https://spdx.org/licenses/MIT.html) license.
