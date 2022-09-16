# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import os
from pathlib import Path
import time
import sys

import pytest

from env_manager.manager import Manager


TESTS_DIR = Path(__file__).parent.absolute()
ENV_FILES = TESTS_DIR / "env_files"
ENV_FILES_CONDA_LIKE = ENV_FILES / "conda-like-files"
ENV_FILES_VENV = ENV_FILES / "venv-files"
BACKENDS = [
    (
        ("venv", None),
        "pip",
        ["packaging"],
        ["foo"],
        (
            "Could not find a version that satisfies the requirement foo",
            "WARNING: Skipping foo as it is not installed",
        ),
    ),
    (
        ("conda-like", os.environ.get("ENV_BACKEND_EXECUTABLE")),
        "python",
        ["packaging"],
        ["foo"],
        ("libmamba Could not solve for environment specs", "Nothing to do"),
    ),
]


if os.name == "nt":
    BASE_IMPORT_EXPORT_FILENAME = "win"
elif sys.platform.startswith("linux"):
    BASE_IMPORT_EXPORT_FILENAME = "linux"
else:
    BASE_IMPORT_EXPORT_FILENAME = "macos"

IMPORT_EXPORT_BACKENDS = [
    (
        ("venv", None),
        str(ENV_FILES_VENV / "venv_import_env.txt"),
        str(ENV_FILES_VENV / "venv_export_env.txt"),
    ),
    (
        ("conda-like", os.environ.get("ENV_BACKEND_EXECUTABLE")),
        str(
            ENV_FILES_CONDA_LIKE / f"{BASE_IMPORT_EXPORT_FILENAME}_conda_import_env.yml"
        ),
        str(
            ENV_FILES_CONDA_LIKE / f"{BASE_IMPORT_EXPORT_FILENAME}_conda_export_env.yml"
        ),
    ),
]


def wait_until(condition, interval=0.1, timeout=1, **kwargs):
    start = time.time()
    while not condition(**kwargs) and time.time() - start < timeout:
        time.sleep(interval)


def package_installed(manager_instance, installed_packages):
    package_list = manager_instance.list()
    for package in installed_packages:
        return package in " ".join(package_list)


def packages_uninstalled(manager_instance, installed_packages):
    package_list = manager_instance.list()
    for package in installed_packages:
        return package not in " ".join(package_list)


@pytest.fixture
def manager_instance(request, tmp_path):
    backend, executable = request.param
    envs_directory = tmp_path / "envs"
    env_directory = envs_directory / f"test_{backend}"
    if backend == "conda-like":
        envs_directory.mkdir(parents=True)
    else:
        env_directory.mkdir(parents=True)

    manager_instance = Manager(
        backend=backend, env_directory=str(env_directory), executable_path=executable
    )
    yield manager_instance
    manager_instance.delete_environment()


@pytest.mark.parametrize(
    "manager_instance,initial_package,installed_packages,errored_packages," "messages",
    BACKENDS,
    indirect=["manager_instance"],
)
def test_manager_backends(
    manager_instance, initial_package, installed_packages, errored_packages, messages
):
    # Create an environment with Python in it
    manager_instance.create_environment(packages=["python"])
    initial_list = manager_instance.list()

    # List packages
    assert initial_package in initial_list["packages"]
    assert len(initial_list) == 2
    assert len(initial_list["packages"]) > 0
    assert len(initial_list["packages"][initial_package]) == 4
    assert initial_list["environment"] == str(env_directory)

    # Install a new package in the created environment
    install_result = manager_instance.install(packages=installed_packages, force=True)
    assert install_result[0]

    # Check package was installed
    wait_until(
        package_installed,
        manager_instance=manager_instance,
        installed_packages=installed_packages,
    )

    # Uninstall the new package
    uninstall_result = manager_instance.uninstall(
        packages=installed_packages, force=True
    )
    assert uninstall_result[0]

    # Check package was uninstalled
    wait_until(
        packages_uninstalled,
        manager_instance=manager_instance,
        installed_packages=installed_packages,
    )

    # Try to install unexisting package
    install_error_message, uninstall_warning_message = messages
    error_result, error_message = manager_instance.install(
        packages=errored_packages, force=True
    )
    assert not error_result
    assert install_error_message in error_message

    # Try to uninstall unexisting package
    warning_result, subprocess_result = manager_instance.uninstall(
        packages=errored_packages, force=True
    )
    assert warning_result
    assert (
        uninstall_warning_message in subprocess_result.stdout + subprocess_result.stderr
    )

<<<<<<< HEAD

@pytest.mark.parametrize(
    "manager_instance,initial_import_path,expected_export_path",
    IMPORT_EXPORT_BACKENDS,
    indirect=["manager_instance"],
)
def test_manager_backends_import_export(
    manager_instance, initial_import_path, expected_export_path, tmp_path
):
    # Import environment definition
    import_result = manager_instance.import_environment(initial_import_path)
    print(import_result[1])
    assert import_result[0]
    wait_until(
        package_installed,
        manager_instance=manager_instance,
        installed_packages=["packaging"],
    )

    # Install packaging 21.0
    manager_instance.install(["packaging<=21.0"])

    # Export environment and check if is the expected one
    export_path_dir = tmp_path / "exported"
    export_path_dir.mkdir()
    if manager_instance.backend_instance.ID == "venv":
        export_path_file = export_path_dir / "exported_file.txt"
    else:
        export_path_file = export_path_dir / "exported_file.yml"

    export_result = manager_instance.export_environment(str(export_path_file))
    print(export_result[1])
    assert export_result[0]
    assert export_path_file.exists()

    with open(expected_export_path) as expected_export_path_file:
        expected_export = expected_export_path_file.readlines()
        expected_export.sort()

    with open(export_path_file) as generated_export_path_file:
        generated_export = generated_export_path_file.readlines()
        generated_export.sort()

    assert generated_export == expected_export
=======
    # Delete the environment
    error_result, error_message = manager.delete_environment()
    assert not error_result
>>>>>>> 6ad2377... delete environment
