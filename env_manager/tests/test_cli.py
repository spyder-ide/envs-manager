# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import os
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
    "update",
    "list",
    "list-environments",
]

BACKENDS = [
    ("venv", [""], "test_env"),
    (
        "conda-like",
        ["Transaction finished", "Executing transaction: ...working... done"],
        "test_env",
    ),
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


@pytest.mark.parametrize("backend", BACKENDS)
def test_cli(tmp_path, backend):
    backend_value, create_result, list_env_result = backend
    backends_root_path = tmp_path / "backends"
    backends_root_path.mkdir(parents=True)
    os.environ["BACKENDS_ROOT_PATH"] = str(backends_root_path)

    # Check environment creation
    create_output = subprocess.check_output(
        " ".join(
            ["env-manager", f"-b={backend_value}", f"-en={list_env_result}", "create"]
        ),
        shell=True,
    )
    assert any(
        [
            expected_create_result in str(create_output)
            for expected_create_result in create_result
        ]
    )

    # Check environment listing
    list_env_output = subprocess.check_output(
        " ".join(
            [
                "env-manager",
                f"-b={backend_value}",
                f"-en=test_create",
                "list-environments",
            ]
        ),
        shell=True,
    )
    assert list_env_result in str(list_env_output)
