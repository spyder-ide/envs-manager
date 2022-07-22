# SPDX-FileCopyrightText: 2022-present Spyder Development Team and env-manager contributors
#
# SPDX-License-Identifier: MIT

import argparse
import os
import os.path as osp
import uuid

from env_manager.manager import Manager


def main(args=None):
    parser = argparse.ArgumentParser(prog=__name__,
                                    description='Manage a virtual Python '
                                                'environment in a target '
                                                'directory.')
    parser.add_argument('-b', '--backend',
                        default=os.environ.get('ENV_BACKEND', 'mamba'),
                        choices=list(Manager.BACKENDS.keys()),
                        help='The implementation to '
                             'create/manage a virtual '
                             'Python environment in the given '
                             'directory.')
    parser.add_argument('-ed', '--env_directory',
                        default=os.environ.get(
                            'ENV_DIR',
                            osp.join(os.getcwd(), 'envs', str(uuid.uuid4()))
                        ),
                        help='A directory where the virtual environment '
                             'is or will be located following the structure '
                             '<base path>/envs/<env name>.')

    main_subparser = parser.add_subparsers(title='commands', dest='command')
    # Create env
    parser_create = main_subparser.add_parser('create',
                                              help='Create a virtual Python '
                                                   'environment in the target '
                                                   'directory.')
    parser_create.add_argument('--packages', nargs='+',
                               help='List of packages to install')
    parser_create.add_argument('--channels', nargs='+',
                               help='List of channels from where to install')

    # Install packages
    parser_install = main_subparser.add_parser('install',
                                               help='Install packages in the '
                                                    'virtual Python '
                                                    'environment placed in the '
                                                    'target directory.')
    parser_install.add_argument('packages', nargs='+',
                                help='List of packages to install')
    parser_install.add_argument('--channels', nargs='+',
                                help='List of channels from where to install')

    # Uninstall packages
    parser_uninstall = main_subparser.add_parser('uninstall',
                                                 help='Uninstall packages in the '
                                                      'virtual Python '
                                                      'environment placed in the '
                                                      'target directory.')
    parser_uninstall.add_argument('packages', nargs='+',
                                  help='List of packages to uninstall')

    # List packages
    parser_list = main_subparser.add_parser('list',
                                            help='List packages available in the '
                                                 'virtual Python '
                                                 'environment placed in the '
                                                 'target directory.')


    options = parser.parse_args(args)
    print(options)
    manager = Manager(backend=options.backend,
                      env_directory=options.env_directory)
    
    if options.command == 'create':
        manager.create_environment(packages=options.packages or ['python'],
                                   channels=options.channels)
    elif options.command == 'install':
        manager.install(packages=options.packages)
    elif options.command == 'uninstall':
        manager.uninstall(packages=options.packages)
    elif options.command == 'list':
        manager.list()
