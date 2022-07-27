# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import os.path as osp

from env_manager.api import EnvManagerInstance


class MambaInterface(EnvManagerInstance):
    ID = "mamba"

    def validate(self):
        try:
            import mamba

            return True
        except:
            return False

    def create_environment(
        self, environment_path, packages=(), channels=("conda-forge",)
    ):
        from mamba.api import create

        base_prefix = osp.dirname(osp.dirname(environment_path))
        environment_name = osp.basename(environment_path)
        create(environment_name, packages, channels, base_prefix=base_prefix)

    def delete_environment(self, environment_path):
        raise NotImplementedError()

    def activate_environment(self):
        raise NotImplementedError()

    def deactivate_environment(self):
        raise NotImplementedError()

    def export_environment(self, environment_path, export_file_path):
        raise NotImplementedError()

    def import_environment(self, environment_path, import_file_path):
        raise NotImplementedError()

    def install_packages(
        self, environment_path, packages, channels=("conda-forge",), force=False
    ):
        from mamba.api import install

        base_prefix = osp.dirname(osp.dirname(environment_path))
        environment_name = osp.basename(environment_path)
        install(environment_name, packages, channels, base_prefix=base_prefix)

    def uninstall_packages(self, environment_path, packages, force=False):
        from mamba.api import MambaSolver

        base_prefix = osp.dirname(osp.dirname(environment_path))
        environment_name = osp.basename(environment_path)
        # TODO: Check https://github.com/mamba-org/mamba/blob/41d99c81d9652f73e38227d1b35cb3ff9b09b206/mamba/mamba/mamba.py#L130
        # and https://github.com/mamba-org/mamba/blob/da44aadfaf88dfa3ce21656d671682626379cea6/mamba/mamba/api.py#L116

    def list_packages(self, environment_path):
        from mamba.utils import get_installed_packages

        _, result = get_installed_packages(environment_path)
        list_result = list(result["packages"].keys())
        print(*list_result, sep="\n")
        return list_result
