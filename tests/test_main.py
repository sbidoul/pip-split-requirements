# SPDX-FileCopyrightText: 2023-present Stéphane Bidoul <stephane.bidoul@acsone.eu>
# SPDX-License-Identifier: MIT

import textwrap
from pathlib import Path
from unittest.mock import create_autospec

import pytest
from typer.testing import CliRunner

from pip_split_requirements.__main__ import app
from pip_split_requirements._split_requirements import GroupSpec, split_requirements


def test_cli_basic(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("pkga\n")
    split_requirements_mock = create_autospec(split_requirements)
    monkeypatch.setattr(
        "pip_split_requirements.__main__.split_requirements",
        split_requirements_mock,
    )
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["--prefix", "prefix", "requirements.txt"])
    assert result.exit_code == 0
    assert split_requirements_mock.call_args[0] == (
        [Path("requirements.txt")],
        [GroupSpec(name="other", pattern=".*")],
    )


def test_cli_pyproject_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("pkga\n")
    (tmp_path / "requirements-test.txt").write_text("pkgb\n")
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent(
            """\
            [tool.pip-split-requirements]
            prefix = "reqs-group"
            group_specs = [
                "ab:^pkg[ab]$",
                "c:^pkgc$",
            ]
            remove_empty = true
            requirements_files = ["requirements.txt", "requirements-test.txt"]
            """,
        ),
    )
    split_requirements_mock = create_autospec(split_requirements)
    monkeypatch.setattr(
        "pip_split_requirements.__main__.split_requirements",
        split_requirements_mock,
    )
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["-r", str(tmp_path)])
    assert result.exit_code == 0
    assert split_requirements_mock.call_args[0] == (
        [
            Path("requirements.txt"),
            Path("requirements-test.txt"),
        ],
        [
            GroupSpec(name="ab", pattern="^pkg[ab]$"),
            GroupSpec(name="c", pattern="^pkgc$"),
            GroupSpec(name="other", pattern=".*"),
        ],
    )
    assert split_requirements_mock.call_args[1] == {
        "prefix": "reqs-group",
        "remove_empty": True,
        "project_root": tmp_path,
    }
