# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import subprocess

import pytest


SUBCOMMANDS = [
    "",
    "create",
    "delete",
    "activate",
    "deactivate",
    "export",
    "import",
    "install",
    "uninstall",
    "list",
]

BACKENDS = [("venv", ""), ("conda-like", "Transaction finished")]


@pytest.mark.parametrize("subcommand", SUBCOMMANDS)
def test_cli_help(subcommand):
    if subcommand:
        subprocess.run(
            ["env-manager", subcommand, "--help"],
            check=True,
        )
    else:
        subprocess.run(
            ["env-manager", "--help"],
            check=True,
        )


@pytest.mark.parametrize("backend", BACKENDS)
def test_cli_create(tmp_path, backend):
    backend_value, result = backend
    envs_directory = tmp_path / "envs"
    envs_directory.mkdir(parents=True)
    env_directory = envs_directory / "test_create"
    create_output = subprocess.check_output(
        " ".join(
            ["env-manager", f"-b={backend_value}", f"-ed={env_directory}", "create"]
        ),
        shell=True,
    )
    assert result in str(create_output)
