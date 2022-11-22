# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT


class EnvManagerInstance:
    ID = ""

    def __init__(self, environment_path, external_executable=None):
        self.environment_path = environment_path
        self.external_executable = external_executable
        self.executable_variant = None
        assert self.validate(), f"{self.ID} backend unavailable!"

    def validate(self):
        pass

    def create_environment(self, packages=None, channels=None):
        raise NotImplementedError()

    def delete_environment(self):
        raise NotImplementedError()

    def activate_environment(self):
        raise NotImplementedError()

    def deactivate_environment(self):
        raise NotImplementedError()

    def export_environment(self, export_file_path=None):
        raise NotImplementedError()

    def import_environment(self, import_file_path):
        raise NotImplementedError()

    def install_packages(
        self,
        packages,
        channels=None,
        force=False,
        capture_output=False,
    ):
        raise NotImplementedError()

    def uninstall_packages(self, packages, force=False, capture_output=False):
        raise NotImplementedError()

    def update_packages(self, packages, force=False, capture_output=False):
        raise NotImplementedError()

    def list_packages(self):
        raise NotImplementedError()
