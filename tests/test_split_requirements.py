# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@acsone.eu>
# SPDX-License-Identifier: MIT

import textwrap
from pathlib import Path

import pytest

from pip_split_requirements import (
    GroupSpec,
    SplitRequirementsUnmatchedLineError,
    split_requirements,
)


def test_basic(tmp_path: Path) -> None:
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        textwrap.dedent(
            """\
                # comment
                --index-url https://pypi.org/simple
                pkga
                pkgb
                other
                pkgc
                stuff
            """,
        ),
    )
    group_prefix = "group"
    output_path = tmp_path / "output"
    output_path.mkdir()
    split_requirements(
        [requirements_file],
        [
            GroupSpec(name="ab", pattern="^pkg[ab]$"),
            GroupSpec(name="c", pattern="^pkgc$"),
            GroupSpec(name="other", pattern=".*"),
        ],
        str(output_path / group_prefix),
        header=None,
    )
    assert len(list(output_path.iterdir())) == 3
    assert (output_path / f"{group_prefix}-ab.txt").read_text() == textwrap.dedent(
        """\
            --index-url https://pypi.org/simple
            pkga
            pkgb
        """,
    )
    assert (output_path / f"{group_prefix}-c.txt").read_text() == textwrap.dedent(
        """\
            --index-url https://pypi.org/simple
            pkgc
        """,
    )
    assert (output_path / f"{group_prefix}-other.txt").read_text() == textwrap.dedent(
        """\
            --index-url https://pypi.org/simple
            other
            stuff
        """,
    )


def test_unmatched_line(tmp_path: Path) -> None:
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        textwrap.dedent(
            """\
                pkga
                other
            """,
        ),
    )
    with pytest.raises(SplitRequirementsUnmatchedLineError):
        split_requirements(
            [requirements_file],
            [
                GroupSpec(name="a", pattern="^pkg[ab]$"),
            ],
            "reqgroup",
        )


def test_nested(tmp_path: Path) -> None:
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        textwrap.dedent(
            """\
                pkga
                -r ./nestedreqs.txt
            """,
        ),
    )
    (tmp_path / "nestedreqs.txt").write_text("pkgb\n")
    prefix = "reqgroup"
    split_requirements(
        [requirements_file],
        [
            GroupSpec(name="a", pattern="^pkga$"),
            GroupSpec(name="b", pattern="^pkgb$"),
        ],
        str(tmp_path / prefix),
        header=None,
    )
    assert (tmp_path / f"{prefix}-a.txt").read_text() == "pkga\n"
    assert (tmp_path / f"{prefix}-b.txt").read_text() == "pkgb\n"


def test_no_match(tmp_path: Path) -> None:
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        textwrap.dedent(
            """\
                pkga
            """,
        ),
    )
    prefix = "reqgroup"
    group_b = tmp_path / f"{prefix}-b.txt"
    group_b.touch()
    split_requirements(
        [requirements_file],
        [
            GroupSpec(name="a", pattern="^pkga$"),
            GroupSpec(name="b", pattern="^pkgb$"),
        ],
        str(tmp_path / prefix),
        header=None,
    )
    assert (tmp_path / f"{prefix}-a.txt").read_text() == "pkga\n"
    assert not group_b.exists(), "group b should have been removed"


def test_multiple_files(tmp_path: Path) -> None:
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        textwrap.dedent(
            """\
                pkga
                other1
            """,
        ),
    )
    requirements_file2 = tmp_path / "requirements2.txt"
    requirements_file2.write_text(
        textwrap.dedent(
            """\
                pkgb
                other2
            """,
        ),
    )
    prefix = "reqgroup"
    split_requirements(
        [requirements_file, requirements_file2],
        [
            GroupSpec(name="a", pattern="^pkga$"),
            GroupSpec(name="b", pattern="^pkgb$"),
            GroupSpec(name="other", pattern=".*"),
        ],
        str(tmp_path / prefix),
        header=None,
    )
    assert (tmp_path / f"{prefix}-a.txt").read_text() == "pkga\n"
    assert (tmp_path / f"{prefix}-b.txt").read_text() == "pkgb\n"
    assert (tmp_path / f"{prefix}-other.txt").read_text() == "other1\nother2\n"


def test_header(tmp_path: Path) -> None:
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(
        textwrap.dedent(
            """\
                pkga
            """,
        ),
    )
    prefix = "reqgroup"
    split_requirements(
        [requirements_file],
        [
            GroupSpec(name="other", pattern=".*"),
        ],
        str(tmp_path / prefix),
    )
    assert (tmp_path / f"{prefix}-other.txt").read_text() == textwrap.dedent(
        """\
            # Generated by pip-split-requirements
            # from requirements.txt.
            # Do not edit.
            pkga
        """
    )
