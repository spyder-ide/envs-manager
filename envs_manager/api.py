# SPDX-FileCopyrightText: 2022-present Spyder Development Team and envs-manager contributors
#
# SPDX-License-Identifier: MIT

# Standard library imports
import subprocess


def run_command(command, capture_output=True, run_env=None):
    """
    Run commands using `subprocess.run`

    Parameters
    ----------
    command : list[str]
        List of string arguments that conform the command to be executed.
    capture_output : bool, optional
        If the output (stdout and stderr) of the command should be stored. The default is True.
    run_env : dict, optional
        Process environment to use when running the command. The default is None.

    Returns
    -------
    result : subprocess.CompletedProcess
        The completed process result object.

    """
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
