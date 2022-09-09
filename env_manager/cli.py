# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import argparse
import os
import uuid
from pathlib import Path

from env_manager.manager import Manager


def main(args=None):
    parser = argparse.ArgumentParser(
        prog=__name__,
        description="Manage a virtual Python " "environment in a target " "directory.",
    )
    parser.add_argument(
        "-b",
        "--backend",
        default=os.environ.get("ENV_BACKEND", "venv"),
        choices=list(Manager.BACKENDS.keys()),
        help="The implementation to "
        "create/manage a virtual "
        "Python environment in the given "
        "directory.",
    )
    parser.add_argument(
        "-ed",
        "--env_directory",
        default=os.environ.get("ENV_DIR", Path.cwd() / "envs" / str(uuid.uuid4())),
        help="A directory where the virtual environment is or will be located following the structure <base path>/envs/<env name>.",
    )

    main_subparser = parser.add_subparsers(title="commands", dest="command")

    # Create env
    parser_create = main_subparser.add_parser(
        "create",
        help="Create a virtual Python environment in the target directory.",
    )
    parser_create.add_argument(
        "--packages", nargs="+", help="List of packages to install."
    )
    parser_create.add_argument(
        "--channels", nargs="+", help="List of channels from where to install."
    )

    # Delete env
    parser_delete = main_subparser.add_parser(
        "delete", help="Delete a virtual Python environment in the target directory."
    )

    # Activate env
    parser_activate = main_subparser.add_parser(
        "activate",
        help="Activate the virtual Python environment in the target directory.",
    )

    # Deactivate env
    parser_deactivate = main_subparser.add_parser(
        "deactivate",
        help="Deactivate the virtual Python environment in the target directory.",
    )

    # Export env
    parser_export = main_subparser.add_parser(
        "export",
        help="Export a virtual Python environment in the target directory to a file.",
    )
    parser_export.add_argument(
        "export_file_path", help="File path to export the environment."
    )

    # Import env
    parser_import = main_subparser.add_parser(
        "import",
        help="Import a virtual Python environment in the target directory from a file.",
    )
    parser_import.add_argument(
        "import_file_path", help="File path from where to import the environment."
    )

    # Install packages
    parser_install = main_subparser.add_parser(
        "install",
        help="Install packages in the "
        "virtual Python "
        "environment placed in the "
        "target directory.",
    )
    parser_install.add_argument(
        "packages", nargs="+", help="List of packages to install."
    )
    parser_install.add_argument(
        "--channels", nargs="+", help="List of channels from where to install."
    )

    # Uninstall packages
    parser_uninstall = main_subparser.add_parser(
        "uninstall",
        help="Uninstall packages in the "
        "virtual Python "
        "environment placed in the "
        "target directory.",
    )
    parser_uninstall.add_argument(
        "packages", nargs="+", help="List of packages to uninstall."
    )

    # List packages
    parser_list = main_subparser.add_parser(
        "list",
        help="List packages available in the "
        "virtual Python "
        "environment placed in the "
        "target directory.",
    )

    options = parser.parse_args(args)
    print(options)
    executable_path = os.environ.get("ENV_BACKEND_EXECUTABLE")
    manager = Manager(
        backend=options.backend,
        env_directory=options.env_directory,
        executable_path=executable_path,
    )

    if options.command == "create":
        manager.create_environment(
            packages=options.packages or ["python"], channels=options.channels
        )
    elif options.command == "delete":
        manager.delete_environment()
    elif options.command == "activate":
        manager.activate()
    elif options.command == "deactivate":
        manager.deactivate()
    elif options.command == "export":
        manager.export_environment(options.export_file_path)
    elif options.command == "import":
        manager.import_environment(options.import_file_path)
    elif options.command == "install":
        manager.install(packages=options.packages)
    elif options.command == "uninstall":
        manager.uninstall(packages=options.packages)
    elif options.command == "list":
        manager.list()
