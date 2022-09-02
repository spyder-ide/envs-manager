# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import os
import time

import pytest

from env_manager.manager import Manager


BACKENDS = [
    (
        "venv",
        "pip",
        ["packaging"],
        ["packagingg"],
        "Could not find a version that satisfies the requirement packagingg",
        None,
    ),
    (
        "conda-like",
        "python",
        ["packaging"],
        ["packagingg"],
        "libmamba Could not solve for environment specs",
        os.environ.get("ENV_BACKEND_EXECUTABLE"),
    ),
]


def wait_until(condition, interval=0.1, timeout=1):
    start = time.time()
    while not condition() and time.time() - start < timeout:
        time.sleep(interval)


@pytest.mark.parametrize(
    "backend,initial_package,installed_packages,errored_packages,"
    "error_message,executable",
    BACKENDS,
)
def test_manager_backends(
    backend,
    initial_package,
    installed_packages,
    errored_packages,
    error_message,
    executable,
    tmp_path,
):
    envs_directory = tmp_path / "envs"
    env_directory = envs_directory / f"test_{backend}"
    if backend == "conda-like":
        envs_directory.mkdir(parents=True)
    else:
        env_directory.mkdir(parents=True)

    manager = Manager(
        backend=backend, env_directory=env_directory, executable_path=executable
    )

    # Create an environment with Python in it
    manager.create_environment(packages=["python"])
    initial_list = manager.list()
    assert initial_package in " ".join(initial_list)

    # Install a new package in the created environment
    install_result = manager.install(packages=installed_packages, force=True)
    assert install_result[0]

    def package_installed():
        package_list = manager.list()
        for package in installed_packages:
            return package in " ".join(package_list)

    wait_until(package_installed)

    # Uninstall the new package
    uninstall_result = manager.uninstall(packages=installed_packages, force=True)
    assert uninstall_result[0]

    def packages_uninstalled():
        package_list = manager.list()
        for package in installed_packages:
            return package not in " ".join(package_list)

    wait_until(packages_uninstalled)

    # Try to install unexisting package
    error_result, message = manager.install(packages=errored_packages, force=True)
    assert not error_result
    assert error_message in message

    # Try to uninstall unexisting package
    # error_result, message = manager.uninstall(packages=errored_packages, force=True)
    # assert not error_result
    # assert error_message in message
