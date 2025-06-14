# SPDX-FileCopyrightText: 2022-present Spyder Development Team and envs-manager contributors
#
# SPDX-License-Identifier: MIT

from __future__ import annotations
import subprocess
from typing import TypedDict

import requests

PYPI_API_PACKAGE_INFO_URL = "https://pypi.org/pypi/{package_name}/json"
ANACONDA_API_PACKAGE_INFO = "https://api.anaconda.org/package/{channel}/{package_name}"


def run_command(command, capture_output=True, run_env=None, cwd=None):
    """
    Run commands using `subprocess.run`

    Parameters
    ----------
    command : list[str]
        List of string arguments that conform the command to be executed.
    capture_output : bool, optional
        If the output (stdout and stderr) of the command should be stored. The default
        is True.
    run_env : dict, optional
        Process environment to use when running the command. The default is None.

    Returns
    -------
    result : subprocess.CompletedProcess
        The completed process result object.

    """
    if capture_output:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            check=True,
            text=True,
            env=run_env,
            cwd=cwd,
        )
    else:
        result = subprocess.run(
            command, stderr=subprocess.PIPE, check=True, text=True, env=run_env, cwd=cwd
        )
    return result


def get_package_info(package_name, channel=None):
    """
    Get package information from the PyPI JSON API and fallback to the
    Anaconda package info API endpoint if needed and a channel is provided.

    Parameters
    ----------
    package_name : str
        Package name to query.
    channel : str, optional
        In case of fallback to the Anaconda endpoint check package info for
        the given package channel. The default is None.

    Returns
    -------
    package_info : dict
        Information about the package (e.g. metadata like its summary).
    """
    package_info_url = PYPI_API_PACKAGE_INFO_URL.format(package_name=package_name)
    package_info = requests.get(package_info_url).json()

    # Here the `message` key is checked since the PyPI JSON API endpoint returns
    # `{"message": "Not Found"}` in case a package was not found.
    # The fallback to the Ananconda API package info endpoint is only done if a `channel` is provided
    # Without a channel the Anaconda endpoint can't be used.
    if "message" in package_info and channel:
        package_info_url = ANACONDA_API_PACKAGE_INFO.format(
            channel=channel, package_name=package_name
        )
        package_info = {"info": requests.get(package_info_url).json()}
    elif "message" in package_info:
        package_info = None
    return package_info


class BackendActionResult(TypedDict):
    """Dictionary to report the result of a backend's action."""

    status: bool
    """True if the action was successful, False otherwise."""

    output: str
    """Action's output."""


class BackendInstance:
    ID = ""

    def __init__(
        self,
        environment_path: str,
        envs_directory: str,
        external_executable: str | None = None,
    ):
        self.environment_path = environment_path
        self.envs_directory = envs_directory
        self.external_executable = external_executable
        self.executable_variant = None
        assert self.validate(), f"{self.ID} backend unavailable!"

    @property
    def python_executable_path(self) -> str:
        raise NotImplementedError

    def validate(self) -> bool:
        pass

    def create_environment(
        self,
        packages: list[str] | None = None,
        channels: list[str] | None = None,
        force: bool = False,
    ) -> BackendActionResult:
        raise NotImplementedError

    def delete_environment(self, force: bool = False) -> BackendActionResult:
        raise NotImplementedError

    def activate_environment(self):
        raise NotImplementedError

    def deactivate_environment(self):
        raise NotImplementedError

    def export_environment(
        self, export_file_path: str | None = None
    ) -> BackendActionResult:
        raise NotImplementedError

    def import_environment(
        self, import_file_path: str, force: bool = False
    ) -> BackendActionResult:
        raise NotImplementedError

    def install_packages(
        self,
        packages: list[str],
        channels: list[str] | None = None,
        force: bool = False,
        capture_output: bool = False,
    ) -> BackendActionResult:
        raise NotImplementedError

    def uninstall_packages(
        self, packages: list[str], force: bool = False, capture_output: bool = False
    ) -> BackendActionResult:
        raise NotImplementedError

    def update_packages(
        self, packages: list[str], force: bool = False, capture_output: bool = False
    ) -> BackendActionResult:
        raise NotImplementedError

    def list_packages(self) -> BackendActionResult:
        raise NotImplementedError

    def list_environments(self) -> BackendActionResult:
        raise NotImplementedError
