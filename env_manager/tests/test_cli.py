# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import subprocess

import pytest


SUBCOMMANDS = [
    "",
    "create",
    "install",
    "uninstall",
    "list",
]


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


def test_cli_create(tmp_path):
    envs_directory = tmp_path / "envs"
    env_directory = envs_directory / "test_create"
    env_directory.mkdir(parents=True)
    create_output = subprocess.check_output(
        ["env-manager", "-b=mamba", f"-ed={env_directory}", "create"]
    )
    assert "Transaction finished" in str(create_output)
