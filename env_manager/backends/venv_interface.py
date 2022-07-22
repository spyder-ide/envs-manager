# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

from env_manager.api import EnvManagerInstance

class VEnvInterface(EnvManagerInstance):
    ID = 'venv'

    def validate(self):
        pass

    def create_environment(self, environment_path, packages=None, channels=None):
        raise NotImplementedError()

    def delete_environment(self, environment_path):
        raise NotImplementedError()

    def activate_environment(self):
        raise NotImplementedError()
    
    def deactivate_environment(self):
        raise NotImplementedError()

    def export_environment(self, environment_path):
        raise NotImplementedError()

    def import_environment(self, environment_path):
        raise NotImplementedError()

    def install_packages(self, environment_path, packages, channels=None):
        raise NotImplementedError()

    def uninstall_packages(self, environment_path, packages):
        raise NotImplementedError()
    
    def list_packages(self, environment_path):
        raise NotImplementedError()

