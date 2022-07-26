# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT


class EnvManagerInstance:
    ID = ""

    def __init__(self, executable_path=None):
        self.executable = executable_path
        assert self.validate(), f"{self.ID} backend unavailable!"

    def validate(self):
        pass

    def create_environment(self, environment_path, packages=None, channels=None):
        raise NotImplementedError()

    def delete_environment(self, environment_path):
        raise NotImplementedError()

    def activate_environment(self, environment_path):
        raise NotImplementedError()

    def deactivate_environment(self, environment_path):
        raise NotImplementedError()

    def export_environment(self, environment_path, export_file_path):
        raise NotImplementedError()

    def import_environment(self, environment_path, import_file_path):
        raise NotImplementedError()

    def install_packages(self, environment_path, packages, channels=None):
        raise NotImplementedError()

    def uninstall_packages(self, environment_path, packages, force=False):
        raise NotImplementedError()

    def list_packages(self, environment_path):
        raise NotImplementedError()
