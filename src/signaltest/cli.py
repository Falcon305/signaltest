import argparse
import json

from signaltest import __version__
from signaltest.baseline.store import BaselineStore


def main(argv=None):
    parser = argparse.ArgumentParser(prog="signaltest")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("version")
    list_cmd = sub.add_parser("baselines")
    list_cmd.add_argument("path")
    show_cmd = sub.add_parser("show")
    show_cmd.add_argument("path")
    show_cmd.add_argument("case")
    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0

    if args.command == "baselines":
        for case_key, record in sorted(BaselineStore(args.path).load().items()):
            print(f"{case_key}  n={len(record.get('scores', []))}  model={record.get('model')}")
        return 0

    if args.command == "show":
        record = BaselineStore(args.path).load().get(args.case)
        if record is None:
            print(f"no baseline for {args.case}")
            return 1
        print(json.dumps(record, indent=2, sort_keys=True))
        return 0

    parser.print_help()
    return 0
