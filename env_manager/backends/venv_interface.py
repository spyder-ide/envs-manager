# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import os.path as osp
import shutil
import subprocess

from env_manager.api import EnvManagerInstance


class VEnvInterface(EnvManagerInstance):
    ID = "venv"

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
        raise NotImplementedError()

    def import_environment(self, environment_path, import_file_path):
        raise NotImplementedError()

    def install_packages(self, environment_path, packages, channels=None, force=False):
        executable_path = osp.join(environment_path, "Scripts", "python.exe")
        result = subprocess.check_output(
            [executable_path, "-m", "pip", "install"] + packages
        ).decode("utf-8")
        print(result)
        return result.split("\r\n")

    def uninstall_packages(self, environment_path, packages, force=False):
        executable_path = osp.join(environment_path, "Scripts", "python.exe")
        result = subprocess.check_output(
            [executable_path, "-m", "pip", "uninstall", "-y"] + packages
        ).decode("utf-8")
        print(result)
        return result.split("\r\n")

    def list_packages(self, environment_path):
        executable_path = osp.join(environment_path, "Scripts", "python.exe")
        result = subprocess.check_output([executable_path, "-m", "pip", "list"]).decode(
            "utf-8"
        )
        print(result)
        return result.split("\r\n")
