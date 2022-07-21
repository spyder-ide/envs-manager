# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import time

import pytest

from env_manager.manager import Manager


# TODO: Add VENV and MICROMAMBA backends
BACKENDS = [('MAMBA', 'mamba')]


def wait_until(condition, interval=0.1, timeout=1):
  start = time.time()
  while not condition() and time.time() - start < timeout:
    time.sleep(interval)


@pytest.mark.parametrize('backend,package', BACKENDS)
def test_manager_backends(backend, package, tmp_path):
    envs_directory = tmp_path / "envs"
    env_directory = envs_directory / f"test_{backend}"
    env_directory.mkdir(parents=True)

    manager = Manager(backend=backend, env_directory=env_directory)

    # Create an environment with Python in it
    manager.create(packages=['python'])
    initial_list = manager.list()
    assert 'python' in ' '.join(initial_list)

    # Install a new package in the created environment
    manager.install(packages=[package])
    def package_installed():
        package_list = manager.list()
        return package in ' '.join(package_list)
    wait_until(package_installed)

    # TODO: Uninstall package from the created environment
    # manager.uninstall(packages=[package])
    # def package_uninstalled():
    #     package_list = manager.list()
    #     return package not in ' '.join(package_list)
    # wait_until(package_uninstalled)