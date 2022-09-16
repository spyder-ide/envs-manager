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
        ["foo"],
        (
            "Could not find a version that satisfies the requirement foo",
            "WARNING: Skipping foo as it is not installed",
        ),
        None,
    ),
    (
        "conda-like",
        "python",
        ["packaging"],
        ["foo"],
        ("libmamba Could not solve for environment specs", "Nothing to do"),
        os.environ.get("ENV_BACKEND_EXECUTABLE"),
    ),
]


def wait_until(condition, interval=0.1, timeout=1):
    start = time.time()
    while not condition() and time.time() - start < timeout:
        time.sleep(interval)


@pytest.mark.parametrize(
    "backend,initial_package,installed_packages,errored_packages,"
    "messages,executable",
    BACKENDS,
)
def test_manager_backends(
    backend,
    initial_package,
    installed_packages,
    errored_packages,
    messages,
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
        backend=backend, env_directory=str(env_directory), executable_path=executable
    )

    # Create an environment with Python in it
    manager.create_environment(packages=["python"])
    initial_list = manager.list()

    # List packages
    assert initial_package in initial_list["packages"]
    assert len(initial_list) == 2
    assert len(initial_list["packages"]) > 0
    assert len(initial_list["packages"][initial_package]) == 4
    assert initial_list["environment"] == str(env_directory)

    # Install a new package in the created environment
    install_result = manager.install(packages=installed_packages, force=True)
    assert install_result[0]

    def package_installed():
        package_list = manager.list()
        for package in installed_packages:
            return package in package_list

    wait_until(package_installed)

    # Uninstall the new package
    uninstall_result = manager.uninstall(packages=installed_packages, force=True)
    assert uninstall_result[0]

    def packages_uninstalled():
        package_list = manager.list()
        for package in installed_packages:
            return package not in package_list

    wait_until(packages_uninstalled)

    # Try to install unexisting package
    install_error_message, uninstall_warning_message = messages
    error_result, error_message = manager.install(packages=errored_packages, force=True)
    assert not error_result
    assert install_error_message in error_message

    # Try to uninstall unexisting package
    warning_result, subprocess_result = manager.uninstall(
        packages=errored_packages, force=True
    )
    assert warning_result
    assert (
        uninstall_warning_message in subprocess_result.stdout + subprocess_result.stderr
    )

    # Delete the environment
    error_result, error_message = manager.delete_environment()
    assert not error_result
