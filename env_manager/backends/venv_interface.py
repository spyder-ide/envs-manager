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

    def _run_command(self, command):
        run_env = os.environ.copy()
        run_env["PIP_REQUIRE_VIRTUALENV"] = "true"
        return subprocess.run(
            command, capture_output=True, check=True, text=True, env=run_env
        )

    def validate(self):
        try:
            import venv

            return True
        except ImportError:
            return False

    def create_environment(self, environment_path, packages=None, channels=None):
        from venv import EnvBuilder

        builder = EnvBuilder(with_pip=True)
        builder.create(environment_path)
        if packages:
            packages.remove("python")
            if len(packages) > 0:
                self.install_packages(environment_path, packages=packages)

    def delete_environment(self, environment_path):
        shutil.rmtree(environment_path)

    def activate_environment(self, environment_path):
        raise NotImplementedError()

    def deactivate_environment(self, environment_path):
        raise NotImplementedError()

    def export_environment(self, environment_path, export_file_path):
        if os.name == "nt":
            executable_path = Path(environment_path) / "Scripts" / "python.exe"
        else:
            executable_path = Path(environment_path) / "bin" / "python"
        try:
            command = [str(executable_path), "-m", "pip", "list", "--format=freeze"]
            result = self._run_command(command)
            with open(export_file_path, "w") as exported_file:
                exported_file.write(result.stdout)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def import_environment(self, environment_path, import_file_path):
        self.create_environment(environment_path)
        if os.name == "nt":
            executable_path = Path(environment_path) / "Scripts" / "python.exe"
        else:
            executable_path = Path(environment_path) / "bin" / "python"
        try:
            command = [
                str(executable_path),
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

    def install_packages(self, environment_path, packages, channels=None, force=False):
        if os.name == "nt":
            executable_path = Path(environment_path) / "Scripts" / "python.exe"
        else:
            executable_path = Path(environment_path) / "bin" / "python"
        try:
            command = [str(executable_path), "-m", "pip", "install"] + packages
            result = self._run_command(command)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def uninstall_packages(self, environment_path, packages, force=False):
        if os.name == "nt":
            executable_path = Path(environment_path) / "Scripts" / "python.exe"
        else:
            executable_path = Path(environment_path) / "bin" / "python"
        try:
            command = [str(executable_path), "-m", "pip", "uninstall"]
            if force:
                command += ["-y"]
            command += packages
            result = self._run_command(command)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def list_packages(self, environment_path):
        if os.name == "nt":
            executable_path = Path(environment_path) / "Scripts" / "python.exe"
        else:
            executable_path = Path(environment_path) / "bin" / "python"

        result = subprocess.check_output(
            [str(executable_path), "-m", "pip", "list"]
        ).decode("utf-8")
        result = result.split("\r\n")
        print(result)
        environment = environment_path
        ret = {}
        final_return = dict(environment=environment, packages=ret)
        for i in range(2, len(result) - 1):
            package_parts = result[i].split()
            dicc = dict(
                name=package_parts[0],
                version=package_parts[1],
                build=("None" if len(package_parts) <= 2 else package_parts[2]),
                channel=("None" if len(package_parts) <= 3 else package_parts[3]),
            )

            ret[package_parts[0]] = dicc

        return final_return
