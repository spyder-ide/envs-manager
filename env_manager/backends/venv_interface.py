# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import os
import shutil
import subprocess
from pathlib import Path

from env_manager.api import EnvManagerInstance


class VEnvInterface(EnvManagerInstance):
    ID = "venv"

    def _run_command(self, command, capture_output=True):
        run_env = os.environ.copy()
        run_env["PIP_REQUIRE_VIRTUALENV"] = "true"
        if capture_output:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                check=True,
                text=True,
                env=run_env,
            )
        else:
            result = subprocess.run(
                command, stderr=subprocess.PIPE, check=True, text=True, env=run_env
            )
        return result

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

    def create_environment(self, packages=None, channels=None):
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
                self.install_packages(packages=packages)

    def delete_environment(self):
        shutil.rmtree(self.environment_path)

    def activate_environment(self):
        raise NotImplementedError()

    def deactivate_environment(self):
        raise NotImplementedError()

    def export_environment(self, export_file_path):
        try:
            command = [self.executable_path, "-m", "pip", "list", "--format=freeze"]
            result = self._run_command(command)
            with open(export_file_path, "w") as exported_file:
                exported_file.write(result.stdout)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def import_environment(self, import_file_path):
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
            package_info = package.split()
            formatted_package = dict(name=package_info[0], version=package_info[1])
            formatted_packages[package_info[0]] = formatted_package

        print(result.stdout)
        return formatted_list
