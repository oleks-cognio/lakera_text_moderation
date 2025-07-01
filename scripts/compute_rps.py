import sys
import fileinput
import re
from collections import Counter
from datetime import datetime
from typing import Iterable, List

def parse_timestamps(log_lines: Iterable[str]) -> List[datetime]:
    timestamps: List[datetime] = []
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    for line in log_lines:
        for match in pattern.finditer(line):
            ts_str = match.group(0)
            try:
                ts = datetime.fromisoformat(ts_str)
                timestamps.append(ts)
            except ValueError:
                continue
    return timestamps


def compute_rps(timestamps: List[datetime]) -> None:
    """Compute and print requests-per-second from a list of datetime objects."""
    counts = Counter(ts.strftime("%Y-%m-%dT%H:%M:%S") for ts in timestamps)
    for second, count in sorted(counts.items()):
        print(f"{second}: {count} req/s")


def main() -> None:
    """Read log lines from stdin or files, parse timestamps, and compute RPS."""
    input_lines = fileinput.input(files=sys.argv[1:] or ("-",))
    timestamps = parse_timestamps(input_lines)
    if not timestamps:
        print("No valid timestamps found.", file=sys.stderr)
        sys.exit(1)
    compute_rps(timestamps)

if __name__ == "__main__":
    main()