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
        try:
            subprocess.check_output(command, stderr=subprocess.PIPE)
            return (True, "")
        except Exception as e:
            error = e.stderr
            return (False, error)

    def delete_environment(self, environment_path):
        try:
            subprocess.check_output(
                [self.executable, "remove", "-p", environment_path, "-y"],
                stderr=subprocess.PIPE,
            )
            return (True, "")
        except Exception as e:
            return (False, e.stderr)

    def activate_environment(self, environment_path):
        raise NotImplementedError()

    def deactivate_environment(self, environment_path):
        raise NotImplementedError()

    def export_environment(self, environment_path, export_file_path):
        raise NotImplementedError()

    def import_environment(self, environment_path, import_file_path):
        raise NotImplementedError()

    def install_packages(
        self, environment_path, packages, channels=["conda-forge"], force=False
    ):
        command = [self.executable, "install", "-p", environment_path] + packages
        if force:
            command + ["-y"]
        if channels:
            channels = ["-c"] + channels
        result = subprocess.check_call(command)
        print(result)

    def uninstall_packages(self, environment_path, packages, force=False):
        command = [self.executable, "remove", "-p", environment_path] + packages
        if force:
            command + ["-y"]
        result = subprocess.check_call(command)
        print(result)

    def list_packages(self, environment_path):
        result = subprocess.check_output(
            [self.executable, "list", "-p", environment_path]
        ).decode("utf-8")
        print(result)
        return result.split("\r\n")
