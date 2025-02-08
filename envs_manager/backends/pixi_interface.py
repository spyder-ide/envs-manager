# SPDX-FileCopyrightText: 2022-present Spyder Development Team and envs-manager contributors
#
# SPDX-License-Identifier: MIT

import logging
import os
from pathlib import Path
import shutil
import subprocess

from packaging.version import parse

from envs_manager.backends.api import BackendInstance, BackendActionResult, run_command


logger = logging.getLogger("envs-manager")


class PixiInterface(BackendInstance):
    ID = "pixi"

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
                if parse(version) >= parse("0.40.3"):
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
