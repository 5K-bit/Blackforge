#!/usr/bin/env python3
"""BlackForge contract evaluation suite.

Separately runnable from `pytest`: validates that every installed BlackForge
template, when generated, actually conforms to the OBEOS manifest contract
(blackforge.core.manifest) and passes the environment doctor — not just that
it builds and imports (tests/test_generated_builds.py already covers that).

This is NOT a benchmark of agent behavior. It's a scaffold/contract
conformance check: for each `obeos-*` template, generate a sample project
and verify its manifest is valid, its `component_type` matches what the
template name promises, and (for templates that ship a pyproject.toml) that
it still builds as a wheel and imports cleanly in isolation.

Usage:
    python eval/run_eval.py [--templates obeos-service,obeos-worker] [--skip-build] [--json report.json]

Exit code is non-zero if any template fails any check, so this is CI-usable
on its own, independent of the regular `pytest` run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Make the sibling `blackforge` package importable when this script is run
# directly (not installed), regardless of caller cwd.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from blackforge.core.generator import GenerationError, generate_project  # noqa: E402
from blackforge.core.manifest import ALLOWED_COMPONENTS, validate_manifest  # noqa: E402
from blackforge.core.doctor import run_doctor  # noqa: E402
from blackforge.core.templates import list_templates  # noqa: E402

# Template name -> the component_type its generated obeos.manifest.json must declare.
# Only templates that ship a manifest are in scope for contract evaluation;
# the generic `cli`/`fastapi`/`python-package` templates have no OBEOS manifest
# and are intentionally excluded.
TEMPLATE_COMPONENT_TYPE = {
    "obeos-agent": "agent",
    "obeos-connector": "connector",
    "obeos-device": "device",
    "obeos-event-consumer": "event-consumer",
    "obeos-hud": "hud",
    "obeos-service": "service",
    "obeos-skill": "skill",
    "obeos-worker": "worker",
}

assert set(TEMPLATE_COMPONENT_TYPE.values()) <= ALLOWED_COMPONENTS


@dataclass(slots=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass(slots=True)
class TemplateReport:
    template: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


def _check_manifest(destination: Path, template: str) -> list[CheckResult]:
    checks: list[CheckResult] = []
    manifest_path = destination / "obeos.manifest.json"
    if not manifest_path.is_file():
        checks.append(CheckResult("manifest_present", False, f"{manifest_path} does not exist"))
        return checks
    checks.append(CheckResult("manifest_present", True, str(manifest_path)))

    report = validate_manifest(manifest_path)
    checks.append(
        CheckResult(
            "manifest_valid",
            report.valid,
            "; ".join(report.errors) if report.errors else "no errors",
        )
    )

    expected = TEMPLATE_COMPONENT_TYPE.get(template)
    if expected is not None:
        actual = report.component_type
        checks.append(
            CheckResult(
                "component_type_matches_template",
                actual == expected,
                f"expected '{expected}', got '{actual}'",
            )
        )

    if report.warnings:
        # Warnings don't fail the check, but are surfaced for visibility.
        checks.append(CheckResult("manifest_warnings", True, "; ".join(report.warnings)))

    return checks


def _check_doctor(destination: Path) -> CheckResult:
    results = run_doctor(destination)
    manifest_check = next((c for c in results if c.name == "manifest"), None)
    if manifest_check is None:
        return CheckResult("doctor_manifest_check", False, "doctor did not report a manifest check")
    return CheckResult("doctor_manifest_check", manifest_check.ok, manifest_check.detail)


def _check_build(destination: Path, tmp_root: Path) -> CheckResult:
    pyproject = destination / "pyproject.toml"
    if not pyproject.is_file():
        return CheckResult("builds_and_imports", True, "skipped — no pyproject.toml (doc-only template)")

    output_dir = tmp_root / "wheels"
    build = subprocess.run(
        [sys.executable, "-I", "-m", "build", "--wheel", "--no-isolation", "--outdir", str(output_dir), str(destination)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if build.returncode != 0:
        return CheckResult("builds_and_imports", False, (build.stdout + build.stderr)[-500:])

    wheels = list(output_dir.glob("*.whl"))
    if not wheels:
        return CheckResult("builds_and_imports", False, "build succeeded but produced no .whl")

    installed = tmp_root / "installed"
    with zipfile.ZipFile(wheels[0]) as archive:
        archive.extractall(installed)
    modules = [p.name for p in installed.iterdir() if p.is_dir() and (p / "__init__.py").exists()]
    if not modules:
        return CheckResult("builds_and_imports", False, "wheel contains no importable package")

    check = subprocess.run(
        [
            sys.executable, "-I", "-c",
            "import importlib,sys;sys.path.insert(0,sys.argv[1]);[importlib.import_module(m) for m in sys.argv[2:]]",
            str(installed), *modules,
        ],
        cwd=tmp_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if check.returncode != 0:
        return CheckResult("builds_and_imports", False, (check.stdout + check.stderr)[-500:])
    return CheckResult("builds_and_imports", True, f"imported: {', '.join(modules)}")


def evaluate_template(template: str, tmp_root: Path, skip_build: bool) -> TemplateReport:
    report = TemplateReport(template=template)
    project_dir = tmp_root / f"gen-{template}"
    project_dir.mkdir(parents=True, exist_ok=True)
    try:
        result = generate_project(template, "eval-sample", output_dir=project_dir)
    except (GenerationError, ValueError) as exc:
        report.checks.append(CheckResult("generation", False, str(exc)))
        return report
    report.checks.append(CheckResult("generation", True, str(result.destination)))

    if template not in TEMPLATE_COMPONENT_TYPE:
        report.checks.append(CheckResult("manifest_present", True, "skipped — template has no OBEOS manifest"))
    else:
        report.checks.extend(_check_manifest(result.destination, template))
        report.checks.append(_check_doctor(result.destination))

    if not skip_build:
        report.checks.append(_check_build(result.destination, project_dir))

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates", help="Comma-separated template names to evaluate (default: all installed templates).")
    parser.add_argument("--skip-build", action="store_true", help="Skip the wheel-build/import check.")
    parser.add_argument("--json", type=Path, help="Write a JSON report to this path.")
    args = parser.parse_args(argv)

    available = list_templates()
    templates = args.templates.split(",") if args.templates else available
    unknown = sorted(set(templates) - set(available))
    if unknown:
        print(f"Unknown template(s): {', '.join(unknown)}. Available: {', '.join(available)}", file=sys.stderr)
        return 2

    reports: list[TemplateReport] = []
    with tempfile.TemporaryDirectory(prefix="blackforge-eval-") as tmp:
        tmp_root = Path(tmp)
        for template in templates:
            reports.append(evaluate_template(template, tmp_root, args.skip_build))

    _print_report(reports)

    if args.json:
        args.json.write_text(
            json.dumps([{"template": r.template, "ok": r.ok, "checks": [asdict(c) for c in r.checks]} for r in reports], indent=2),
            encoding="utf-8",
        )
        print(f"\nJSON report written to {args.json}")

    failed = [r for r in reports if not r.ok]
    if failed:
        print(f"\n{len(failed)}/{len(reports)} template(s) failed contract evaluation: {', '.join(r.template for r in failed)}")
        return 1
    print(f"\nAll {len(reports)} template(s) passed contract evaluation.")
    return 0


def _print_report(reports: list[TemplateReport]) -> None:
    for report in reports:
        status = "PASS" if report.ok else "FAIL"
        print(f"\n=== {report.template} — {status} ===")
        for check in report.checks:
            mark = "ok  " if check.ok else "FAIL"
            print(f"  [{mark}] {check.name}: {check.detail}")


if __name__ == "__main__":
    raise SystemExit(main())
