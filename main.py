import click
import config as _Config
from typing import List
import Logger as _Logger
from poc.poc_factory import get_metadata
import sys
import time
import os
import platform
from fuzzer import fuzzing


@click.group(help=_Config.__description__)
@click.version_option(version=_Config.__version__, prog_name=_Config.__prog__)
def cli():
    pass


def is_windows():
    return platform.system() == "Windows"


def check_write_permissions(file_paths):
    no_write_permission_files = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            if not os.access(file_path, os.W_OK):
                no_write_permission_files.append(file_path)

    return no_write_permission_files


def timed(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("\n" + "=" * 40)
        print(f"\033[1;32m{func.__name__} finished in {elapsed_time:.2f} seconds.\033[0m")
        print("=" * 40 + "\n")
        return result

    return wrapper


@cli.command()
# The config file is in a json format which indicates that includes all the testing configurations
@click.option('-i',
              '--iteration',
              type=click.INT,
              default=4,
              help='the max iteartion time.'
              )
@click.option('-hr',
              '--hook_result_file',
              type=click.STRING,
              default="/tmp/hook.log",
              help='the enter hook result file.'
              )
@click.option('-ir',
              '--if_result_file',
              type=click.STRING,
              default="/tmp/if.log",
              help='the if hook result file.'
              )
@click.option('-cr',
              '--call_stack_result_file',
              type=click.STRING,
              default="/tmp/callstack.log",
              help='the call stack result file.'
              )
@click.option('-or',
              '--oracle_result_file',
              type=click.STRING,
              default="/tmp/oracle.log",
              help='the oracle hook result file.'
              )
@click.option('-app',
              '--application_name',
              type=click.STRING,
              default=None,
              help='which application you want to test.'
              )
@timed
def main(iteration, hook_result_file, if_result_file,
         call_stack_result_file, oracle_result_file, application_name):
    if application_name is None:
        print(" [*] application_name not filled")
        exit(0)
    else:
        metadata = get_metadata(application_name)

    if not is_windows():
        print(" [*] check write log permission on linux")
        noperm = check_write_permissions([hook_result_file, if_result_file, call_stack_result_file, oracle_result_file])
        if len(noperm):
            for file in noperm:
                print(f"{file} no write permission")
            sys.exit(0)
    else:
        print(" [*] del log file on windows")
        os.system("del .\\tmp\\*.log")
    callchain = os.environ.get("CALLCHAIN", None)
    if callchain:
        metadata.call_chain = callchain
    print(f" [*] new callchain {metadata.call_chain}")
    final_prompt, prompt_successful = fuzzing(
        metadata.call_chain,
        metadata.container_name,
        iteration,
        hook_result_file,
        call_stack_result_file,
        metadata.connect_with_auth,
        metadata.oracle_json,
        if_result_file,
        metadata.if_json,
        oracle_result_file,
        metadata.dsc_json,

    )
    print("*" * 10 + "FINAL PROMPT" + "*" * 10)
    print(final_prompt)
    print("*" * 10 + "exploration successful" + "*" * 10)
    print(prompt_successful)


if __name__ == '__main__':
    main(sys.argv[1:])
