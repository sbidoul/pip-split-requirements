# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@acsone.eu>
# SPDX-License-Identifier: MIT

import sys
from pathlib import Path
from typing import Any, List, Optional

import typer

from ._split_requirements import GroupSpec, split_requirements

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

app = typer.Typer()


def _parse_group_spec(spec: str) -> GroupSpec:
    name, pattern = spec.split(":", 1)
    return GroupSpec(name=name, pattern=pattern)


def _project_root_callback(
    ctx: typer.Context,
    _param: Any,
    value: Path,
) -> Path:
    """Load default values from pyproject.toml."""
    pyproject_toml_path = value / "pyproject.toml"
    if pyproject_toml_path.is_file():
        ctx.default_map = (
            tomllib.loads(pyproject_toml_path.read_text(encoding="utf-8"))
            .get("tool", {})
            .get("pip-split-requirements", {})
        )
    return value


def _requirement_files_callback(
    ctx: typer.Context,
    param: Any,
    value: Optional[List[Path]],
) -> List[Path]:
    """If requirements_files is not specified, read it from pyproject.toml."""
    if value:
        return value
    assert ctx.default_map is not None
    requirement_files = [
        Path(rf) for rf in ctx.default_map.get("requirements_files", [])
    ]
    if not requirement_files:
        msg = "No requirements files specified."
        raise typer.BadParameter(msg, ctx, param)
    for rf in requirement_files:
        if not rf.is_file():
            msg = f"File {rf} does not exist."
            raise typer.BadParameter(msg, ctx, param)
    return requirement_files


@app.command()
def command(
    requirements_files: Optional[List[Path]] = typer.Argument(  # noqa: B008
        None,
        metavar="REQUIREMENTS_FILE...",
        file_okay=True,
        dir_okay=False,
        exists=True,
        callback=_requirement_files_callback,
        help=(
            "The requirements files to split. "
            "If not specified, they are read from pyproject.toml."
        ),
    ),
    *,
    group_specs: List[str] = typer.Option(  # noqa: B008
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
    project_root: Path = typer.Option(  # noqa: B008
        ".",
        "--project-root",
        "-r",
        # Process this parameter first so we can load default values from pyproject.toml
        is_eager=True,
        callback=_project_root_callback,
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
        help=(
            "The project root directory. "
            "The generated requirements files will be relative to this directory. "
            "Default options and arguments "
            "are read from pyproject.toml in this directory."
        ),
    ),
) -> None:
    """Split a pip requirements file into multiple files according to patterns.

    Patterns are regular expressions against which requirement lines are searched to
    determine if they belong to a group. Group specs are evaluated in order, and the
    first match determines in which group the line goes.

    Comment lines are ignored.

    Option lines are emitted in all groups.
    """
    # We are guaranteed to have a requirements_file because of the
    # _requirement_files_callback.
    assert requirements_files is not None
    parsed_group_specs = [_parse_group_spec(group_spec) for group_spec in group_specs]
    if default_group:
        parsed_group_specs.append(GroupSpec(name="other", pattern=".*"))
    split_requirements(
        requirements_files,
        parsed_group_specs,
        prefix=prefix,
        remove_empty=remove_empty,
        project_root=project_root,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
