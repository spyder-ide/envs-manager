# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

from env_manager.backends.venv_interface import VEnvInterface
from env_manager.backends.conda_like_interface import CondaLikeInterface


class Manager:
    """
    Class to handle different Python environment and packages managers implementations.
    """

    BACKENDS = {
        VEnvInterface.ID: VEnvInterface,
        CondaLikeInterface.ID: CondaLikeInterface,
    }

    def __init__(
        self,
        backend,
        root_path=None,
        env_name=None,
        env_directory=None,
        external_executable=None,
    ):
        backend_class = self.BACKENDS[backend]
        if env_directory:
            self.env_directory = str(env_directory)
        elif root_path and env_name:
            self.env_directory = root_path / backend / "envs" / env_name
        else:
            raise Exception(
                "'env_directory' or 'root_path' and 'env_name' should be provided"
            )
        self.backend_instance = backend_class(
            str(self.env_directory), external_executable=str(external_executable)
        )

    def create_environment(self, packages=None, channels=None):
        if channels:
            self.backend_instance.create_environment(packages, channels)
        else:
            self.backend_instance.create_environment(packages)

    def delete_environment(self):
        self.backend_instance.delete_environment()

    def activate(self):
        self.backend_instance.activate_environment()

    def deactivate(self):
        self.backend_instance.deactivate_environment()

    def export_environment(self, export_file_path):
        return self.backend_instance.export_environment(export_file_path)

    def import_environment(self, import_file_path):
        return self.backend_instance.import_environment(import_file_path)

    def install(self, packages=None, channels=None, force=False, capture_output=False):
        if channels:
            return self.backend_instance.install_packages(
                packages=packages,
                channels=channels,
                force=force,
                capture_output=capture_output,
            )
        else:
            return self.backend_instance.install_packages(packages, force=force)

    def uninstall(self, packages, force=False, capture_output=False):
        return self.backend_instance.uninstall_packages(
            packages, force=force, capture_output=capture_output
        )

    def update(self, packages, force=False, capture_output=False):
        return self.backend_instance.update_packages(
            packages, force=force, capture_output=capture_output
        )

    def list(self):
        return self.backend_instance.list_packages()

    def list_environments(self):
        envs_directory = self.env_directory.parent
        environments = {}
        print("Name - Path")
        for env_dir in envs_directory.iterdir():
            if env_dir.is_dir():
                environments[env_dir.name] = str(env_dir)
                print(f"{env_dir.name} - {str(env_dir)}")
        return environments
