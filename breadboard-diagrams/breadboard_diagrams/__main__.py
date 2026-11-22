"""python3 -m breadboard_diagrams circuits/slider-single-usb.json --out output"""

import argparse
import json
import sys

from .model import Circuit, DesignError
from .render import export


def main():
    parser = argparse.ArgumentParser(description="Validate and render a breadboard circuit.")
    parser.add_argument("circuit", help="Circuit JSON file")
    parser.add_argument("--out", default="output", help="Output directory")
    parser.add_argument("--formats", default="svg,png,pdf", help="Comma-separated svg,png,pdf")
    parser.add_argument("--png-scale", type=float, default=2, help="PNG pixels per scene unit")
    parser.add_argument("--check", action="store_true", help="Validate only, no rendering dependencies")
    args = parser.parse_args()
    if args.png_scale <= 0:
        parser.error("--png-scale must be positive")
    try:
        if args.check:
            print(json.dumps(Circuit(args.circuit).validate(), indent=2))
        else:
            print(json.dumps({"files": export(args.circuit, args.out,
                                             args.formats.split(","), args.png_scale)}, indent=2))
    except (DesignError, ValueError, KeyError, FileNotFoundError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
