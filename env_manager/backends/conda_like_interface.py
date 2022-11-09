# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import shutil
import subprocess

from env_manager.api import EnvManagerInstance

MICROMAMBA_VARIANT = "micromamba"
CONDA_VARIANT = "conda"


class CondaLikeInterface(EnvManagerInstance):
    ID = "conda-like"

    def validate(self):
        if self.external_executable:
            command = [self.external_executable, "--version"]
            try:
                result = subprocess.run(
                    command, capture_output=True, check=True, text=True
                )
                version = result.stdout.split()
                if len(version) <= 1:
                    self.executable_variant = MICROMAMBA_VARIANT
                else:
                    self.executable_variant = version[0]
                return True
            except Exception as error:
                print(error.stderr)
        return False

    def create_environment(self, packages=[], channels=["conda-forge"]):
        command = [self.external_executable, "create", "-p", self.environment_path]
        if packages:
            command += packages
        if channels:
            command += ["-c"] + channels
        try:
            result = subprocess.run(
                command, stderr=subprocess.PIPE, check=True, text=True
            )
            print(result.stdout)
            return (True, result)
        except Exception as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def delete_environment(self):
        command = [
            self.external_executable,
            "remove",
            "-p",
            self.environment_path,
            "--all",
            "-y",
        ]
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            print(result.stdout)
            shutil.rmtree(self.environment_path, ignore_errors=True)
            return (True, result)
        except Exception as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def activate_environment(self):
        raise NotImplementedError()

    def deactivate_environment(self):
        raise NotImplementedError()

    def export_environment(self, export_file_path):
        command = [
            self.external_executable,
            "env",
            "export",
            "-p",
            self.environment_path,
        ]
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            with open(export_file_path, "w") as exported_file:
                exported_file.write(result.stdout)
            print(result.stdout)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (False, f"{error.returncode}: {error.stderr}")

    def import_environment(self, import_file_path):
        if self.executable_variant == MICROMAMBA_VARIANT:
            command = [
                self.external_executable,
                "create",
                "-p",
                self.environment_path,
                f"--file={import_file_path}",
            ]
        else:
            command = [
                self.external_executable,
                "env",
                "create",
                "-p",
                self.environment_path,
                f"--file={import_file_path}",
            ]
        try:
            result = subprocess.run(command, capture_output=True, check=True, text=True)
            print(result.stdout)
            return (True, result)
        except subprocess.CalledProcessError as error:
            return (
                False,
                f"{error.returncode}: {error.stderr}\nNote: Importing environments only works for environment definitions created with the same operating system.",
            )

    def install_packages(
        self,
        packages,
        channels=["conda-forge"],
        force=False,
        capture_output=False,
    ):
        if self.executable_variant != MICROMAMBA_VARIANT:
            packages = [f"'{package}'" for package in packages]
        command = [
            self.external_executable,
            "install",
            "-p",
            self.environment_path,
        ] + packages
        if force:
            command += ["-y"]
        if channels:
            channels = ["-c"] + channels
            command += channels
        try:
            if capture_output:
                result = subprocess.run(
                    command, capture_output=True, check=True, text=True
                )
            else:
                result = subprocess.run(
                    command, stderr=subprocess.PIPE, check=True, text=True
                )
            return (True, result)
        except subprocess.CalledProcessError as error:
            formatted_error = f"{error.returncode}: {error.stderr}"
            return (False, formatted_error)

    def uninstall_packages(self, packages, force=False, capture_output=False):
        command = [
            self.external_executable,
            "remove",
            "-p",
            self.environment_path,
        ] + packages
        if force:
            command + ["-y"]
        try:
            if capture_output:
                result = subprocess.run(
                    command, capture_output=capture_output, check=True, text=True
                )
            else:
                result = subprocess.run(
                    command, stderr=subprocess.PIPE, check=True, text=True
                )
            return (True, result)
        except subprocess.CalledProcessError as error:
            if "PackagesNotFoundError" in error.stderr:
                return (True, error)
            formatted_error = f"{error.returncode}: {error.stderr}"
            return (False, formatted_error)

    def update_packages(self, packages, force=False, capture_output=False):
        command = [
            self.external_executable,
            "update",
            "-p",
            self.environment_path,
        ] + packages
        if force:
            command + ["-y"]
        try:
            if capture_output:
                result = subprocess.run(
                    command, capture_output=capture_output, check=True, text=True
                )
                if "All requested packages already installed" in result.stdout:
                    return (False, result.stdout)
            else:
                result = subprocess.run(
                    command, stderr=subprocess.PIPE, check=True, text=True
                )
            return (True, result)
        except subprocess.CalledProcessError as error:
            formatted_error = f"{error.returncode}: {error.stderr}"
            return (False, formatted_error)

    def list_packages(self):
        command = [self.external_executable, "list", "-p", self.environment_path]
        result = subprocess.run(command, capture_output=True, check=True, text=True)
        result_lines = result.stdout.split("\n")

        if self.executable_variant == MICROMAMBA_VARIANT:
            skip_lines = 4
        else:
            skip_lines = 3
        formatted_packages = {}
        formatted_list = dict(
            environment=self.environment_path, packages=formatted_packages
        )

        for package in result_lines[skip_lines:-1]:
            package_info = package.split()
            formatted_package = dict(
                name=package_info[0],
                version=package_info[1],
                build=(None if len(package_info) <= 2 else package_info[2]),
                channel=(None if len(package_info) <= 3 else package_info[3]),
            )
            formatted_packages[package_info[0]] = formatted_package

        print(result.stdout)
        return formatted_list
