# SPDX-FileCopyrightText: 2022-present Spyder Development Team and envs-manager contributors
#
# SPDX-License-Identifier: MIT

import logging
import os
import shutil
import subprocess
from pathlib import Path

from envs_manager.backends.api import (
    BackendActionResult,
    BackendInstance,
    get_package_info,
    run_command,
)


logger = logging.getLogger("envs-manager")


class VEnvInterface(BackendInstance):
    ID = "venv"

    def _run_command(self, command, capture_output=True):
        run_env = os.environ.copy()
        run_env["PIP_REQUIRE_VIRTUALENV"] = "true"
        result = run_command(command, capture_output=capture_output, run_env=run_env)
        return result

    @property
    def python_executable_path(self):
        if os.name == "nt":
            python_executable_path = (
                Path(self.environment_path) / "Scripts" / "python.exe"
            )
        else:
            python_executable_path = Path(self.environment_path) / "bin" / "python"

        return str(python_executable_path)

    def validate(self):
        try:
            import venv  # noqa

            return True
        except ImportError:
            return False

    def create_environment(self, packages=None, channels=None, force=False):
        try:
            from venv import EnvBuilder

            builder = EnvBuilder(with_pip=True)
            builder.create(self.environment_path)
            if packages:
                try:
                    packages.remove("python")
                except ValueError:
                    pass
                possible_pythons = [
                    package
                    for package in packages
                    if package.startswith(("python=", "python<", "python>"))
                ]
                for possible_python in possible_pythons:
                    packages.remove(possible_python)
                if len(packages) > 0:
                    return self.install_packages(packages=packages)
                return BackendActionResult(status=True, output=None)
        except Exception as error:
            return BackendActionResult(status=False, output=str(error))

    def delete_environment(self, force=False):
        try:
            shutil.rmtree(self.environment_path)
            return BackendActionResult(status=True, output=None)
        except Exception as error:
            return BackendActionResult(status=False, output=str(error))

    def activate_environment(self):
        raise NotImplementedError()

    def deactivate_environment(self):
        raise NotImplementedError()

    def export_environment(self, export_file_path=None):
        try:
            command = [
                self.python_executable_path,
                "-m",
                "pip",
                "list",
                "--format=freeze",
                "--not-required",
            ]
            result = self._run_command(command)
            if export_file_path:
                with open(export_file_path, "w") as exported_file:
                    exported_file.write(result.stdout)
            logger.info(result.stdout)
            return BackendActionResult(status=True, output=result.stdout)
        except subprocess.CalledProcessError as error:
            return BackendActionResult(status=False, output=error.stderr)
        except Exception as error:
            return BackendActionResult(status=False, output=str(error))

    def import_environment(self, import_file_path, force=False):
        self.create_environment()
        try:
            command = [
                self.python_executable_path,
                "-m",
                "pip",
                "install",
                "-r",
                import_file_path,
            ]
            result = self._run_command(command)
            logger.info(result.stdout)
            return BackendActionResult(status=True, output=result.stdout)
        except subprocess.CalledProcessError as error:
            return BackendActionResult(status=False, output=error.stderr)
        except Exception as error:
            return BackendActionResult(status=False, output=str(error))

    def install_packages(
        self,
        packages,
        channels=None,
        force=False,
        capture_output=False,
    ):
        try:
            command = [self.python_executable_path, "-m", "pip", "install"] + packages
            result = self._run_command(command, capture_output=capture_output)
            if capture_output:
                logger.info(result.stdout or result.stderr)
            return BackendActionResult(
                status=True, output=result.stdout or result.stderr
            )
        except subprocess.CalledProcessError as error:
            return BackendActionResult(status=False, output=error.stderr)
        except Exception as error:
            return BackendActionResult(status=False, output=str(error))

    def uninstall_packages(self, packages, force=False, capture_output=False):
        try:
            command = [self.python_executable_path, "-m", "pip", "uninstall"]
            if force:
                command += ["-y"]
            command += packages
            result = self._run_command(command, capture_output=capture_output)
            if capture_output:
                logger.info(result.stdout or result.stderr)
            return BackendActionResult(
                status=True, output=result.stdout or result.stderr
            )
        except subprocess.CalledProcessError as error:
            return BackendActionResult(status=False, output=error.stderr)
        except Exception as error:
            return BackendActionResult(status=False, output=str(error))

    def update_packages(self, packages, force=False, capture_output=False):
        try:
            command = [self.python_executable_path, "-m", "pip", "install", "-U"]
            command += packages
            result = self._run_command(command, capture_output=capture_output)
            if capture_output:
                logger.info(result.stdout)
            return BackendActionResult(status=True, output=result.stdout)
        except subprocess.CalledProcessError as error:
            return BackendActionResult(status=False, output=error.stderr)
        except Exception as error:
            return BackendActionResult(status=False, output=str(error))

    def list_packages(self):
        command = [self.python_executable_path, "-m", "pip", "list"]
        result = self._run_command(command)
        result_lines = result.stdout.split("\n")

        formatted_packages = []
        formatted_list = dict(
            environment=self.environment_path, packages=formatted_packages
        )
        for package in result_lines[2:-1]:
            package_name, package_version = package.split()
            package_description = get_package_info(package_name)["info"]["summary"]
            formatted_package = dict(
                name=package_name,
                version=package_version,
                build=None,
                channel=None,
                description=package_description,
                requested=True,
            )
            formatted_packages.append(formatted_package)

        logger.info(result.stdout)
        return BackendActionResult(status=True, output=formatted_list)

    def list_environments(self):
        environments = {}
        first_environment = False
        envs_directory = Path(self.envs_directory)

        logger.info(f"# {self.ID} environments")
        envs_directory.mkdir(parents=True, exist_ok=True)
        for env_dir in envs_directory.iterdir():
            if env_dir.is_dir():
                if not first_environment:
                    first_environment = True
                environments[env_dir.name] = str(env_dir)
                logger.info(f"{env_dir.name} - {str(env_dir)}")

        if not first_environment:
            logger.info(f"No environments found for {self.ID} in {self.envs_directory}")

        return BackendActionResult(status=True, output=environments)
