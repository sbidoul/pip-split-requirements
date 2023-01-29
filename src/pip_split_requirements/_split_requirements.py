# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@acsone.eu>
# SPDX-License-Identifier: MIT

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from ._req_file_parser import (
    NestedRequirementsLine,
    OptionsLine,
    RequirementLine,
    parse,
)


@dataclass
class GroupSpec:
    name: str
    pattern: str


class SplitRequirementsError(Exception):
    pass


class SplitRequirementsUnmatchedLineError(SplitRequirementsError):
    pass


def split_requirements(
    filename: Path,
    group_specs: list[GroupSpec],
    prefix: str,
) -> None:
    """Split a requirements file into multiple files.

    The requirements file is parsed and requirements are assigned to groups according to
    the group_specs patterns. The requirements are then written to files named
    <prefix>-<group_name>.txt.

    Comments are ignored.

    Lines that do not match any group cause a SplitRequirementsError exception to be
    raised.
    """
    options: list[OptionsLine] = []
    groups = defaultdict(list)
    for req_line in parse(str(filename), recurse=True, reqs_only=False):
        if isinstance(req_line, OptionsLine):
            options.append(req_line)
        elif isinstance(req_line, RequirementLine):
            for group_spec in group_specs:
                if re.match(group_spec.pattern, req_line.raw_line):
                    groups[group_spec.name].append(req_line)
                    break
            else:
                msg = f"Requirement {req_line.raw_line} does not match any group"
                raise SplitRequirementsUnmatchedLineError(msg)
        elif isinstance(req_line, NestedRequirementsLine):
            # Since parse will recurse into nested requirements files, we can just
            # ignore these lines.
            pass
        else:
            if req_line.raw_line.startswith("#"):
                continue
            msg = f"Unexpected requirement line type {req_line.raw_line}"
            raise SplitRequirementsError(msg)
    for group_spec in group_specs:
        group_filename = Path(f"{prefix}-{group_spec.name}.txt")
        if group_filename.exists():
            group_filename.unlink()
        if group_spec.name not in groups:
            continue
        with group_filename.open("w") as f:
            for option_line in options:
                f.write(option_line.raw_line + "\n")
            for req_line in groups[group_spec.name]:
                f.write(req_line.raw_line + "\n")
