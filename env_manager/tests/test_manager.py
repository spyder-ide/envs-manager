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
            ["Could not find a version that satisfies the requirement foo"],
            ["WARNING: Skipping foo as it is not installed"],
        ),
        [2, 1, 2],
    ),
    (
        ("conda-like", os.environ.get("ENV_BACKEND_EXECUTABLE")),
        "python",
        ["packaging"],
        ["foo"],
        (
            ["libmamba Could not solve for environment specs", "PackagesNotFoundError"],
            ["Nothing to do", "PackagesNotFoundError"],
        ),
        [2, 1, 4],
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
    assert condition(**kwargs)


def package_installed(manager_instance, installed_packages):
    package_list = manager_instance.list()
    for package in installed_packages:
        return package in package_list["packages"]


def packages_uninstalled(manager_instance, installed_packages):
    package_list = manager_instance.list()
    for package in installed_packages:
        return package not in package_list["packages"]


def check_packages(manager_instance, package, version):
    packages_list = manager_instance.list()
    return (
        package in packages_list["packages"]
        and packages_list["packages"][package]["version"] == version
    )


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
    "manager_instance,initial_package,installed_packages,errored_packages,messages,list_dimensions",
    BACKENDS,
    indirect=["manager_instance"],
)
def test_manager_backends(
    manager_instance,
    initial_package,
    installed_packages,
    errored_packages,
    messages,
    list_dimensions,
):
    # Create an environment with Python in it
    manager_instance.create_environment(packages=["python==3.10"])

    # List packages and check correct list result dimensions
    initial_list = manager_instance.list()
    assert initial_package in initial_list["packages"]
    assert len(initial_list) == list_dimensions[0]
    assert len(initial_list["packages"]) > list_dimensions[1]
    assert len(initial_list["packages"][initial_package]) == list_dimensions[2]

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
    assert any(
        [
            install_expected_error in error_message
            for install_expected_error in install_error_message
        ]
    )

    # Try to uninstall unexisting package
    warning_result, subprocess_result = manager_instance.uninstall(
        packages=errored_packages, force=True, capture_output=True
    )
    print(subprocess_result)
    assert warning_result
    assert any(
        [
            uninstall_expected_error in subprocess_result.stdout
            or uninstall_expected_error in subprocess_result.stderr
            for uninstall_expected_error in uninstall_warning_message
        ]
    )


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
        check_packages,
        manager_instance=manager_instance,
        package="packaging",
        version="21.3",
    )

    # Install packaging 21.0
    channels = None
    if manager_instance.backend_instance.ID == "conda-like":
        channels = ["conda-forge"]
    install_result, message = manager_instance.install(
        ["packaging==21.0"], channels=channels, force=True, capture_output=True
    )
    print(message)
    assert install_result

    # Wait until package is installed
    wait_until(
        check_packages,
        manager_instance=manager_instance,
        package="packaging",
        version="21.0",
    )

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
        expected_export = set()
        for expected_line in expected_export_path_file.readlines():
            if "=" in expected_line and "ca-certificates" not in expected_line:
                expected_export.add(expected_line.strip())

    with open(export_path_file) as generated_export_path_file:
        generated_export = set()
        for generated_line in generated_export_path_file.readlines():
            if "=" in generated_line and "ca-certificates" not in generated_line:
                generated_export.add(generated_line.strip())

    assert generated_export == expected_export
