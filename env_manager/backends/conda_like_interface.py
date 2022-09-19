# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import subprocess

from env_manager.api import EnvManagerInstance


class CondaLikeInterface(EnvManagerInstance):
    ID = "conda-like"

    def validate(self):
        if self.executable:
            subprocess.check_output([self.executable, "-h"]).decode("utf-8")
            return True
        return False

    def create_environment(
        self, environment_path, packages=[], channels=["conda-forge"]
    ):
        command = [self.executable, "create", "-p", environment_path]
        if packages:
            command += packages
        if channels:
            command += ["-c"] + channels
        result = subprocess.check_call(command)
        print(result)

    def delete_environment(self, environment_path):
        result = subprocess.check_call(
            [self.executable, "remove", "-p", environment_path, "-y"]
        )
        print(result)

    def activate_environment(self, environment_path):
        raise NotImplementedError()

    def deactivate_environment(self, environment_path):
        raise NotImplementedError()

    def export_environment(self, environment_path, export_file_path):
        command = [str(self.executable), "env", "export", "-p", environment_path]
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            with open(export_file_path, "w") as exported_file:
                exported_file.write(result.stdout)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def import_environment(self, environment_path, import_file_path):
        command = [
            str(self.executable),
            "create",
            "-p",
            environment_path,
            f"--file={import_file_path}",
        ]
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (
                False,
                f"{error.returncode}: {error.stderr}\nNote: Importing environments only works for environment definitions created with the same operating system.",
            )

    def install_packages(
        self, environment_path, packages, channels=["conda-forge"], force=False
    ):
        command = [
            str(self.executable),
            "install",
            "-p",
            str(environment_path),
        ] + packages
        if force:
            command += ["-y"]
        if channels:
            channels = ["-c"] + channels
            command += channels
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def uninstall_packages(self, environment_path, packages, force=False):
        command = [
            str(self.executable),
            "remove",
            "-p",
            str(environment_path),
        ] + packages
        if force:
            command + ["-y"]
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def list_packages(self, environment_path):
        result = subprocess.check_output(
            [self.executable, "list", "-p", environment_path]
        ).decode("utf-8")
        print(result)
        return result.split("\r\n")
