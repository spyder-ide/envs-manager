# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

from env_manager.backends.mamba_interface import MambaInterface
from env_manager.backends.venv_interface import VEnvInterface
from env_manager.backends.micromamba_interface import MicromambaInterface


class Manager:
    BACKENDS = {
        MambaInterface.ID: MambaInterface,
        VEnvInterface.ID: VEnvInterface,
        MicromambaInterface.ID: MicromambaInterface
    }

    def __init__(self, backend, env_directory, executable_path=None):
        backend_class = self.BACKENDS[backend]
        self.manager_instance = backend_class(executable_path=executable_path)
        self.env_directory = env_directory

    def create_environment(self, packages=None, channels=None):
        if channels:
            self.manager_instance.create_environment(self.env_directory, packages, channels)
        else:
            self.manager_instance.create_environment(self.env_directory, packages)
    
    def install(self, packages=None, channels=None):
        if channels:
            self.manager_instance.install_packages(self.env_directory, packages, channels)
        else:
            self.manager_instance.install_packages(self.env_directory, packages)
    
    def uninstall(self, packages):
        self.manager_instance.uninstall_packages(self.env_directory, packages)

    def list(self):
        return self.manager_instance.list_packages(self.env_directory)

