# SPDX-FileCopyrightText: 2022-present Spyder Development Team and envs-manager contributors
#
# SPDX-License-Identifier: MIT

import os
import shutil
import subprocess
from pathlib import Path

import requests

from envs_manager.api import EnvManagerInstance, run_command

PYPI_API_PACKAGE_INFO_URL = "https://pypi.org/pypi/{package_name}/json"


class VEnvInterface(EnvManagerInstance):
    ID = "venv"

    def _run_command(self, command, capture_output=True):
        run_env = os.environ.copy()
        run_env["PIP_REQUIRE_VIRTUALENV"] = "true"
        result = run_command(command, capture_output=capture_output, run_env=run_env)
        return result

    def _get_package_info(self, package_name):
        package_info_url = PYPI_API_PACKAGE_INFO_URL.format(package_name=package_name)
        package_info = requests.get(package_info_url).json()
        return package_info

    @property
    def executable_path(self):
        if os.name == "nt":
            executable_path = Path(self.environment_path) / "Scripts" / "python.exe"
        else:
            executable_path = Path(self.environment_path) / "bin" / "python"

        return str(executable_path)

    def validate(self):
        try:
            import venv

            return True
        except ImportError:
            return False

    def create_environment(self, packages=None, channels=None, force=False):
        try:
            from venv import EnvBuilder

            builder = EnvBuilder(with_pip=True)
            builder.create(self.environment_path)
            if packages:
                try:
                    packages.remove("python")
                except ValueError:
                    pass
                possible_pythons = [
                    package
                    for package in packages
                    if package.startswith(("python=", "python<", "python>"))
                ]
                for possible_python in possible_pythons:
                    packages.remove(possible_python)
                if len(packages) > 0:
                    return self.install_packages(packages=packages)
                return (True, None)
        except Exception as error:
            return (False, str(error))

    def delete_environment(self, force=False):
        shutil.rmtree(self.environment_path)

    def activate_environment(self):
        raise NotImplementedError()

    def deactivate_environment(self):
        raise NotImplementedError()

    def export_environment(self, export_file_path=None):
        try:
            command = [
                self.executable_path,
                "-m",
                "pip",
                "list",
                "--format=freeze",
                "--not-required",
            ]
            result = self._run_command(command)
            if export_file_path:
                with open(export_file_path, "w") as exported_file:
                    exported_file.write(result.stdout)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def import_environment(self, import_file_path, force=False):
        self.create_environment()
        try:
            command = [
                self.executable_path,
                "-m",
                "pip",
                "install",
                "-r",
                import_file_path,
            ]
            result = self._run_command(command)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def install_packages(
        self,
        packages,
        channels=None,
        force=False,
        capture_output=False,
    ):
        try:
            command = [self.executable_path, "-m", "pip", "install"] + packages
            result = self._run_command(command, capture_output=capture_output)
            print(result.stdout)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def uninstall_packages(self, packages, force=False, capture_output=False):
        try:
            command = [self.executable_path, "-m", "pip", "uninstall"]
            if force:
                command += ["-y"]
            command += packages
            result = self._run_command(command, capture_output=capture_output)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def update_packages(self, packages, force=False, capture_output=False):
        try:
            command = [self.executable_path, "-m", "pip", "install", "-U"]
            command += packages
            result = self._run_command(command, capture_output=capture_output)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def list_packages(self):
        command = [self.executable_path, "-m", "pip", "list"]
        result = self._run_command(command)
        result_lines = result.stdout.split("\n")

        formatted_packages = {}
        formatted_list = dict(
            environment=self.environment_path, packages=formatted_packages
        )
        for package in result_lines[2:-1]:
            package_name, package_version = package.split()
            package_description = self._get_package_info(package_name)["info"][
                "summary"
            ]
            formatted_package = dict(
                name=package_name,
                version=package_version,
                build=None,
                channel=None,
                description=package_description,
                requested=True,
            )
            formatted_packages[package_name] = formatted_package

        print(result.stdout)
        return formatted_list
