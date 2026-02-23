#!/usr/bin/env python3

import argparse
import logging
import sys

from .cmds.build import build
from .cmds.init import init
from .cmds.install import install
from .cmds.run import run
from .cmds.remove import remove
from .cmds.set_template import set_template

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s]: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Автоматически подтверждать все запросы'
    )

    parser = argparse.ArgumentParser(
        prog='pcpm',
        description='pcpm — менеджер проектов'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        required=True,
        metavar='<command>'
    )

    init_parser = subparsers.add_parser(
        'init',
        parents=[common],
        help='Создать новый проект'
    )
    init_parser.add_argument(
        'name',
        nargs='?',
        help='Имя проекта (по умолчанию — имя текущей директории)'
    )
    init_parser.add_argument(
        '-d', '--dir',
        metavar='DIR',
        help='Директория для создания проекта (по умолчанию — текущая)'
    )

    install_parser = subparsers.add_parser(
        'install',
        aliases=['i'],
        parents=[common],
        help='Установить зависимости проекта'
    )
    install_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Принудительно переустановить пакеты, игнорируя текущее состояние'
    )
    install_parser.add_argument(
        'pkg_names',
        nargs='*',
        help='Список пакетов для установки (если не указаны — установить из конфигурации)'
    )

    build_parser = subparsers.add_parser(
        'build',
        aliases=['b'],
        help='Собрать проект'
    )
    build_subparsers = build_parser.add_subparsers(
        dest='build_subcommand',
        help='Подкоманды сборки'
    )

    build_run_parser = build_subparsers.add_parser(
        'run',
        help='Собрать проект и сразу выполнить'
    )
    build_run_parser.add_argument(
        'run_args',
        nargs='*',
        help='Аргументы, передаваемые исполняемому приложению'
    )

    run_parser = subparsers.add_parser(
        'run',
        aliases=['r'],
        parents=[common],
        help='Запустить проект'
    )
    run_parser.add_argument(
        'run_args',
        nargs='*',
        help='Аргументы, передаваемые приложению'
    )

    remove_parser = subparsers.add_parser(
        'remove',
        parents=[common],
        help='Удалить пакеты из проекта'
    )
    remove_parser.add_argument(
        'remove_args',
        nargs='*',
        help='Список пакетов для удаления'
    )

    set_template_parser = subparsers.add_parser(
        'set_template',
        parents=[common],
        help='Создать или обновить шаблон конфигурационного файла config.json'
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == 'init':
        init(name=args.name, dir=args.dir)
    elif args.command == 'install' or args.command == 'i':
        install(args.pkg_names, True if args.force is not None else False)
    elif args.command == 'build' or args.command == 'b':
        if build() and args.build_subcommand == 'run':
            run(args.run_args)
    elif args.command == 'run':
        run(args.run_args)
    elif args.command == "remove":
        remove(args.remove_args)
    elif args.command == "set_template":
        set_template()
    
if __name__ == "__main__":
    main()