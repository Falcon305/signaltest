import argparse
import json
from collections.abc import Sequence
from typing import Optional

from signaltest import __version__
from signaltest.baseline.store import BaselineStore
from signaltest.metrics.base import BOOLEAN, NUMERIC
from signaltest.report import format_report, read_json, to_html, to_markdown
from signaltest.stats.power import advise


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="signaltest")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("version")
    list_cmd = sub.add_parser("baselines")
    list_cmd.add_argument("path")
    show_cmd = sub.add_parser("show")
    show_cmd.add_argument("path")
    show_cmd.add_argument("case")
    rm_cmd = sub.add_parser("rm")
    rm_cmd.add_argument("path")
    rm_cmd.add_argument("case")
    report_cmd = sub.add_parser("report")
    report_cmd.add_argument("path")
    report_cmd.add_argument("--format", choices=["md", "text", "html"], default="md")
    power_cmd = sub.add_parser("power")
    power_cmd.add_argument("path")
    power_cmd.add_argument("case")
    power_cmd.add_argument("--min-effect", type=float, required=True)
    power_cmd.add_argument("--alpha", type=float, default=0.05)
    power_cmd.add_argument("--power", type=float, default=0.8)
    power_cmd.add_argument("--kind", choices=[NUMERIC, BOOLEAN], default=None)
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

    if args.command == "rm":
        store = BaselineStore(args.path)
        data = store.load()
        if args.case not in data:
            print(f"no baseline for {args.case}")
            return 1
        del data[args.case]
        store.save(data)
        print(f"removed {args.case}")
        return 0

    if args.command == "report":
        results = read_json(args.path)
        renderers = {"md": to_markdown, "html": to_html, "text": format_report}
        print(renderers[args.format](results))
        return 0

    if args.command == "power":
        record = BaselineStore(args.path).load().get(args.case)
        if record is None:
            print(f"no baseline for {args.case}")
            return 1
        scores = record.get("scores", [])
        kind = args.kind or _infer_kind(scores)
        n = advise(scores, kind, args.min_effect, args.alpha, args.power)
        print(f"{n} samples per run to detect an effect of {args.min_effect} at power {args.power}")
        return 0

    parser.print_help()
    return 0


def _infer_kind(scores: Sequence[object]) -> str:
    if all(s in (True, False, 0, 1) for s in scores):
        return BOOLEAN
    return NUMERIC
