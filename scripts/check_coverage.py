#!/usr/bin/env python3
"""Per-module coverage gate.

Runs after ``pytest --cov-report=xml`` and parses ``coverage.xml`` to
enforce per-module thresholds **in addition to** the global ``fail_under``
in ``pyproject.toml``. A high overall number must not be allowed to hide
regressions inside a single critical module.

Add new prefixes to :data:`MODULE_GATES` as the project grows. Follow the
ratchet policy: when a module's actual coverage exceeds ``gate + 0.5``,
raise the gate to ``floor(actual) - 0.5`` in the same PR. Gates never
retreat without an explicit governance discussion.

Stdlib only — this script must run before ``uv sync`` in fresh CI shells.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

GLOBAL_GATE = 90.0
"""Global coverage floor (also enforced by ``fail_under`` in pyproject)."""

MODULE_GATES: tuple[tuple[str, float], ...] = (
    # Example. Replace with your project's modules after the first real test pass:
    # ("core/", 90.0),
    # ("cli/", 85.0),
)
"""Per-area gates. ``(prefix, minimum_percent)`` matched against ``<class filename=...>``."""


@dataclass(frozen=True)
class ModuleCoverage:
    prefix: str
    covered: int
    total: int

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 100.0
        return self.covered / self.total * 100.0


@dataclass(frozen=True)
class GateResult:
    coverage: ModuleCoverage
    threshold: float

    @property
    def passed(self) -> bool:
        return self.coverage.percent >= self.threshold


def parse_coverage(path: Path) -> dict[str, tuple[int, int]]:
    """Return per-file ``(covered, total)`` lines from a coverage XML file."""
    tree = ET.parse(path)  # noqa: S314 — produced by our own test run.
    root = tree.getroot()
    out: dict[str, tuple[int, int]] = {}
    for cls in root.iter("class"):
        filename = cls.get("filename", "")
        if not filename:
            continue
        lines_node = cls.find("lines")
        if lines_node is None:
            continue
        total = 0
        covered = 0
        for line in lines_node.findall("line"):
            total += 1
            if int(line.get("hits", "0")) > 0:
                covered += 1
        out[filename] = (covered, total)
    return out


def aggregate(files: dict[str, tuple[int, int]], prefix: str) -> ModuleCoverage:
    covered = 0
    total = 0
    for path, (cv, tv) in files.items():
        if path.startswith(prefix):
            covered += cv
            total += tv
    return ModuleCoverage(prefix=prefix, covered=covered, total=total)


def evaluate_gates(
    files: dict[str, tuple[int, int]],
    gates: Iterable[tuple[str, float]],
) -> list[GateResult]:
    return [GateResult(coverage=aggregate(files, prefix), threshold=threshold) for prefix, threshold in gates]


def global_coverage(files: dict[str, tuple[int, int]]) -> ModuleCoverage:
    covered = sum(cv for cv, _ in files.values())
    total = sum(tv for _, tv in files.values())
    return ModuleCoverage(prefix="<global>", covered=covered, total=total)


def format_summary(global_result: GateResult, module_results: list[GateResult]) -> str:
    lines = ["Coverage gates:", ""]
    header = f"  {'prefix':<30} {'covered/total':>14} {'actual':>8} {'gate':>7} {'status':>8} {'ratchet->':>10}"
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))

    def row(result: GateResult) -> str:
        cov = result.coverage
        status = "ok" if result.passed else "FAIL"
        grid = (int(cov.percent * 2) - 1) / 2
        suggestion = f"{grid:.1f}" if grid > result.threshold else "--"
        return (
            f"  {result.coverage.prefix:<30} "
            f"{cov.covered:>6}/{cov.total:<7} "
            f"{cov.percent:>7.2f}% "
            f"{result.threshold:>6.1f}% "
            f"{status:>8} "
            f"{suggestion:>10}"
        )

    lines.append(row(global_result))
    if module_results:
        lines.append("")
        for result in module_results:
            lines.append(row(result))
    return "\n".join(lines)


def format_failures(failures: list[GateResult]) -> str:
    lines = ["Coverage gate failures:"]
    for f in failures:
        cov = f.coverage
        lines.append(
            f"  {cov.prefix}: {cov.percent:.2f}% < {f.threshold:.1f}% ({cov.covered}/{cov.total} lines covered)"
        )
    return "\n".join(lines)


def run(xml_path: Path) -> int:
    if not xml_path.exists():
        print(f"error: coverage file not found: {xml_path}", file=sys.stderr)
        print("Hint: run `uv run pytest --cov --cov-report=xml` first.", file=sys.stderr)
        return 2

    files = parse_coverage(xml_path)
    global_res = GateResult(coverage=global_coverage(files), threshold=GLOBAL_GATE)
    module_res = evaluate_gates(files, MODULE_GATES)

    print(format_summary(global_res, module_res))

    failures = [r for r in [global_res, *module_res] if not r.passed]
    if failures:
        print("", file=sys.stderr)
        print(format_failures(failures), file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enforce per-module coverage gates on coverage.xml.")
    parser.add_argument(
        "--xml",
        type=Path,
        default=Path("coverage.xml"),
        help="Path to coverage.xml (default: ./coverage.xml).",
    )
    args = parser.parse_args(argv)
    return run(args.xml)


if __name__ == "__main__":
    raise SystemExit(main())
