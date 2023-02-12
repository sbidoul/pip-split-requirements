# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@acsone.eu>
# SPDX-License-Identifier: MIT

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from pip_requirements_parser import RequirementsFile  # type: ignore[import]


@dataclass
class GroupSpec:
    name: str
    pattern: str


class SplitRequirementsError(Exception):
    pass


class SplitRequirementsUnmatchedLineError(SplitRequirementsError):
    pass


def split_requirements(
    filenames: Sequence[Path],
    group_specs: Sequence[GroupSpec],
    *,
    prefix: str,
    header: Optional[str] = (
        "# Generated by pip-split-requirements\n"
        "# from {original_filenames}.\n"
        "# Do not edit."
    ),
    remove_empty: bool = True,
    project_root: Path = Path("."),  # noqa: B008
) -> None:
    """Split a requirements file into multiple files.

    The requirements file is parsed and requirements are assigned to groups according to
    the group_specs patterns. The requirements are then written to files named
    <prefix>-<group_name>.txt.

    Comments are ignored.

    Lines that do not match any group cause a SplitRequirementsError exception to be
    raised.
    """
    req_files = [
        RequirementsFile.from_file(str(filename), include_nested=True)
        for filename in filenames
    ]
    groups = defaultdict(list)
    for req_file in req_files:
        for req_line in req_file.requirements:
            for group_spec in group_specs:
                if re.search(group_spec.pattern, req_line.line):
                    groups[group_spec.name].append(req_line)
                    break
            else:
                msg = f"Requirement {req_line.line} does not match any group"
                raise SplitRequirementsUnmatchedLineError(msg)
    for group_spec in group_specs:
        group_filename = project_root / Path(f"{prefix}-{group_spec.name}.txt")
        if remove_empty and group_spec.name not in groups:
            if group_filename.exists():
                group_filename.unlink()
            continue
        with group_filename.open("w") as f:
            if header:
                original_filenames = ", ".join(str(f.name) for f in filenames)
                f.write(header.format(original_filenames=original_filenames) + "\n")
            for req_file in req_files:
                for option_line in req_file.options:
                    if option_line.options.get("requirements"):
                        continue
                    f.write(option_line.line + "\n")
            for req_line in groups[group_spec.name]:
                f.write(req_line.line + "\n")
