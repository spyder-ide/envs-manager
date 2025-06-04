# SPDX-FileCopyrightText: 2022-present Spyder Development Team and envs-manager contributors
#
# SPDX-License-Identifier: MIT

import json
import logging
import os
from pathlib import Path
import shutil
import subprocess

from packaging.version import parse
from rattler import AboutJson

from envs_manager.backends.api import BackendInstance, BackendActionResult, run_command


logger = logging.getLogger("envs-manager")


class PixiInterface(BackendInstance):
    ID = "pixi"

    def __init__(self, environment_path, envs_directory, external_executable=None):
        super().__init__(environment_path, envs_directory, external_executable)

        # We use this to save the Pixi packages cache directory
        self._cache_dir = None

    @property
    def python_executable_path(self):
        pixi_env_dir = Path() / ".pixi" / "envs" / "default"

        if os.name == "nt":
            python_executable_path = (
                Path(self.environment_path) / pixi_env_dir / "python.exe"
            )
        else:
            python_executable_path = (
                Path(self.environment_path) / pixi_env_dir / "bin" / "python"
            )

        return str(python_executable_path)

    def validate(self):
        if self.external_executable is None:
            cmd_list = ["pixi", "pixi.exe"]
            for cmd in cmd_list:
                if shutil.which(cmd):
                    self.external_executable = shutil.which(cmd)

        if self.external_executable:
            command = [self.external_executable, "--version"]
            try:
                result = run_command(command, capture_output=True)
                version = result.stdout.split()[1]
                if parse(version) >= parse("0.47.0"):
                    return True
            except subprocess.CalledProcessError as error:
                logger.error(error.stderr.strip())
            except Exception as error:
                logger.error(error, exc_info=True)

        return False

    def create_environment(self, packages=None, channels=None, force=False):
        # We need to run `pixi init` first
        init_command = [
            self.external_executable,
            "init",
            # Set all these platforms for the project so that its lock file works in
            # any OS supported by Spyder.
            "--platform",
            "linux-64",
            "--platform",
            "win-64",
            "--platform",
            "osx-64",
            "--platform",
            "osx-arm64",
            self.environment_path,
        ]

        if channels:
            for channel in channels:
                init_command += ["-c"] + [channel]

        try:
            result = run_command(init_command, capture_output=True)
            output = result.stdout or result.stderr
            logger.info(output.strip())
        except subprocess.CalledProcessError as error:
            error_text = error.stderr.strip()
            logger.error(error_text)
            return BackendActionResult(status=False, output=error_text)
        except Exception as error:
            logger.error(error, exc_info=True)
            return BackendActionResult(status=False, output=str(error))

        if packages:
            if not isinstance(packages, list):
                packages = [packages]

            command = [self.external_executable, "add"] + packages
            try:
                result = run_command(
                    command, capture_output=True, cwd=self.environment_path
                )
                output = (result.stdout or result.stderr).strip()
                logger.info(output)
                return BackendActionResult(status=True, output=output)
            except subprocess.CalledProcessError as error:
                error_text = error.stderr.strip()
                logger.error(error_text)
                return BackendActionResult(status=False, output=error_text)
            except Exception as error:
                logger.error(error, exc_info=True)
                return BackendActionResult(status=False, output=str(error))

    def delete_environment(self, force=False):
        # There is no command in Pixi to remove an env, so we rely on the OS
        # for that.
        # TODO: Add validation on Windows when the env is in use
        command = [
            "rmdir" if os.name == "nt" else "rm",
            "/S" if os.name == "nt" else "-r",  # Remove all files and subdirs
            "/Q" if os.name == "nt" else "-f",  # Don't ask
            self.environment_path,
        ]

        try:
            result = run_command(command, capture_output=True)
            logger.info(f"Deleting environment located at {self.environment_path}")
            return BackendActionResult(status=True, output=result.stdout)
        except subprocess.CalledProcessError as error:
            error_text = error.stderr.strip()
            logger.error(error_text)
            return BackendActionResult(status=False, output=error_text)
        except Exception as error:
            logger.error(error, exc_info=True)
            return BackendActionResult(status=False, output=str(error))

    def install_packages(
        self,
        packages,
        channels=None,
        force=False,
        capture_output=False,
    ):
        command = [self.external_executable, "add"] + packages

        try:
            result = run_command(
                command, capture_output=capture_output, cwd=self.environment_path
            )

            output = None
            if capture_output:
                output = (result.stdout or result.stderr).strip()
                logger.info(output)

            return BackendActionResult(status=True, output=output if output else "")
        except subprocess.CalledProcessError as error:
            error_text = error.stderr.strip()
            logger.error(error_text)
            return BackendActionResult(status=False, output=error_text)
        except Exception as error:
            logger.error(error, exc_info=True)
            return BackendActionResult(status=False, output=str(error))

    def uninstall_packages(self, packages, force=False, capture_output=False):
        command = [self.external_executable, "remove"] + packages

        try:
            result = run_command(
                command, capture_output=capture_output, cwd=self.environment_path
            )

            output = None
            if capture_output:
                output = (result.stdout or result.stderr).strip()
                logger.info(output)

            return BackendActionResult(status=True, output=output if output else "")
        except subprocess.CalledProcessError as error:
            error_text = error.stderr.strip()
            logger.error(error_text)
            return BackendActionResult(status=False, output=error_text)
        except Exception as error:
            logger.error(error, exc_info=True)
            return BackendActionResult(status=False, output=str(error))

    def update_packages(self, packages, force=False, capture_output=False):
        command = [self.external_executable, "upgrade"] + packages

        try:
            result = run_command(
                command, capture_output=capture_output, cwd=self.environment_path
            )

            output = None
            if capture_output:
                output = (result.stdout or result.stderr).strip()
                logger.info(output)
                return BackendActionResult(status=True, output=output)
            else:
                return BackendActionResult(status=True, output="")
        except subprocess.CalledProcessError as error:
            error_text = error.stderr.strip()
            logger.error(error_text)
            return BackendActionResult(status=False, output=error_text)
        except Exception as error:
            logger.error(error, exc_info=True)
            return BackendActionResult(status=False, output=str(error))

    def list_packages(self):
        # All packages
        command = [self.external_executable, "list"]
        result = run_command(command, capture_output=True, cwd=self.environment_path)
        result_lines = result.stdout.split("\n")

        # Requsted packages
        requested_command = [self.external_executable, "list", "--explicit"]
        result_requested = run_command(
            requested_command, capture_output=True, cwd=self.environment_path
        )
        packages_requested = result_requested.stdout.split("\n")[1:-1]
        packages_requested = [package.split()[0] for package in packages_requested]

        formatted_packages = []
        formatted_list = dict(
            environment=self.environment_path, packages=formatted_packages
        )

        for package in result_lines[1:-1]:
            package_info = package.split()
            package_name = package_info[0]
            package_version = package_info[1]
            package_build = package_info[2]
            package_channel = package_info[5]
            package_requested = package_name in packages_requested

            package_dir = package_name + "-" + package_version + "-" + package_build
            package_full_info = self._get_package_info(package_dir)
            package_description = (
                package_full_info.description or package_full_info.summary
            )

            # Only take the first sentence of the description and replace eols by
            # spaces
            if package_description:
                package_description = package_description.split(".")[0].replace(
                    "\n", " "
                )

            formatted_package = dict(
                name=package_name,
                version=package_version,
                build=package_build,
                channel=package_channel,
                description=package_description,
                requested=package_requested,
            )
            formatted_packages.append(formatted_package)

        logger.info(result.stdout.strip())
        return BackendActionResult(status=True, output=formatted_list)

    def list_environments(self):
        environments = {}

        logger.info(f"# {self.ID} environments")
        for env_dir_path in Path(self.envs_directory).iterdir():
            environments[env_dir_path.name] = str(env_dir_path)
            logger.info(f"{env_dir_path.name} - {str(env_dir_path)}")

        return BackendActionResult(status=True, output=environments)

    def _get_package_info(self, package_dir):
        """
        Get package information from the Pixi packages cache.

        Parameters
        ----------
        package_dir : str
            Package directory name in the Pixi packages cache.

        Returns
        -------
        package_info : AboutJson
            Py-rattler object with metadata about the package.
        """
        info = None

        if self._cache_dir is None:
            try:
                command = [self.external_executable, "info", "--json"]
                result = run_command(command, capture_output=True)
                self._cache_dir = json.loads(result.stdout).get("cache_dir")
            except subprocess.CalledProcessError as error:
                logger.error(error, exc_info=True)
                return

        if self._cache_dir is not None:
            absolute_package_dir = Path(self._cache_dir) / "pkgs" / package_dir
            info = AboutJson.from_package_directory(str(absolute_package_dir))

        return info
