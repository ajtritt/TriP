import argparse
from importlib.resources import files
import os
import sys

import pprint

from .qc import QCJob
from .workflow import CromwellJob


description = """Command line interface for processing NERSC LDMS data

See nmdcwf <command> --help for command specific options.
"""

epilog = """
Feature requests or bug reports:

 * https://software.nersc.gov/ldms/nersc-ldms/-/issues

"""


class MainCLI:
    def __init__(self):
        # options common for all subcommands

        # main command parser
        parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=epilog
        )

        subparsers = parser.add_subparsers(description="Available subcommands")


        config_file = files(__package__).joinpath('etc/config.toml')
        config = CromwellJob.load_config(config_file)


        commands = { cls.job_type: cls for cls in [QCJob] }
        for cmd, cli in commands.items():
            subparser = subparsers.add_parser(cmd, help=cli.__doc__)
            cli.add_args(subparser)
            cli.add_bp_args(subparser)
            subparser.set_defaults(command=cmd)
            subparser.add_argument("--verbose", "-v", action="count", default=0,
                                                help="repeat (e.g. -vvv) for more output")
        args = parser.parse_args()
        config.update(vars(args))

        if hasattr(args, 'command'):
            if config.get('verbose', 0) > 0:
                pprint.pprint(config, stream=sys.stderr)
            job_dir, job_id = commands[args.command].run(**config)
            if job_id is not None:
                print(job_dir, job_id)
        else:
            parser.print_help()
            exit(1)


def main():
    try:
        cli = MainCLI()
        sys.stdout.flush()
    except BrokenPipeError:
        # dump the remaining output to /dev/null
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
