# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@acsone.eu>
# SPDX-License-Identifier: MIT

from pathlib import Path
from typing import List

import typer

from ._split_requirements import GroupSpec, split_requirements


def _parse_group_spec(spec: str) -> GroupSpec:
    name, pattern = spec.split(":", 1)
    return GroupSpec(name=name, pattern=pattern)


def _main(
    requirements_files: List[Path] = typer.Argument(  # noqa: B008
        ...,
        metavar="REQUIREMENTS_FILE...",
        file_okay=True,
        dir_okay=False,
        exists=True,
    ),
    *,
    group_spec: List[str] = typer.Option(  # noqa: B008
        [],
        "--group-spec",
        "-g",
        help="Group specifications in form name:pattern.",
    ),
    prefix: str = typer.Option(  # noqa: B008
        "requirementsgroup",
        "--prefix",
        "-p",
        help=(
            "Each requirements group file will be named {prefix}-{group_name}.txt. "
            "The prefix can contain path separators, "
            "to generate files into a chosen directory."
        ),
    ),
    default_group: bool = typer.Option(  # noqa: B008
        default=True,
        help=(
            "Automatically append a group named 'other', matching all lines "
            "not matched by other groups."
        ),
    ),
    remove_empty: bool = typer.Option(  # noqa: B008
        default=False,
        help=("Remove empty requirements group files."),
    ),
) -> None:
    """Split a pip requirements file into multiple files according to patterns.

    Patterns are regular expressions against which requirement lines are searched to
    determine if they belong to a group. Group specs are evaluated in order, and the
    first match determines in which group the line goes.

    Comment lines are ignored.

    Option lines are emitted in all groups.
    """
    parsed_group_specs = [_parse_group_spec(spec) for spec in group_spec]
    if default_group:
        parsed_group_specs.append(GroupSpec(name="other", pattern=".*"))
    split_requirements(
        requirements_files,
        parsed_group_specs,
        prefix=prefix,
        remove_empty=remove_empty,
    )


def main() -> None:
    typer.run(_main)


if __name__ == "__main__":
    main()
