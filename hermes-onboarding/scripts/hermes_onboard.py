#!/usr/bin/env python3
"""Idempotent bibliotec onboarding for a Hermes profile.

The command deliberately uses the installed ``hermes`` and ``herdr`` CLIs as
its public control surfaces. It never reads or prints credential files.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


DEFAULT_REPO_URL = "https://github.com/mdc159/bibliotec.git"
DEFAULT_CHECKOUT = Path("~/.claude/skills/library")
MARKER_START = "<!-- bibliotec:hermes-onboarding:start -->"
MARKER_END = "<!-- bibliotec:hermes-onboarding:end -->"
REQUIRED_SKILLS = ("library", "orchestration-playbook")
REQUIRED_COMMANDS = ("git", "hermes")
RECOMMENDED_COMMANDS = ("gh", "herdr", "pi", "uv", "just")


class OnboardingError(RuntimeError):
    """A safe, user-actionable onboarding failure."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass
class Report:
    checkout: str
    hermes_home: str
    checkout_action: str = "unchanged"
    config_action: str = "unchanged"
    bootstrap_action: str = "unchanged"
    skills_verified: list[str] | None = None
    missing_recommended_commands: list[str] | None = None
    smoke_artifact: str | None = None


Runner = Callable[..., CommandResult]


def run_command(
    command: Sequence[str],
    *,
    timeout: int = 120,
    env: dict[str, str] | None = None,
) -> CommandResult:
    completed = subprocess.run(
        list(command),
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
        check=False,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def require_ok(result: CommandResult, action: str) -> CommandResult:
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise OnboardingError(f"{action} failed: {detail}")
    return result


def expand(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def managed_block(bootstrap: str) -> str:
    return f"{MARKER_START}\n{bootstrap.strip()}\n{MARKER_END}"


def extract_bootstrap_stanza(source: str) -> str:
    """Extract the portable stanza between the prompt file's rule markers."""
    lines = source.splitlines()
    markers = [index for index, line in enumerate(lines) if line.strip() == "---"]
    if len(markers) < 2:
        raise OnboardingError("fleet bootstrap file is missing its stanza delimiters")
    stanza = "\n".join(lines[markers[0] + 1 : markers[-1]]).strip()
    if not stanza:
        raise OnboardingError("fleet bootstrap stanza is empty")
    return stanza + "\n"


def upsert_bootstrap(soul_path: Path, bootstrap: str, *, dry_run: bool = False) -> bool:
    """Install or refresh one managed bootstrap block while preserving persona text."""
    original = soul_path.read_text() if soul_path.exists() else ""
    desired_block = managed_block(bootstrap)
    marker_pattern = re.compile(
        rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}", re.DOTALL
    )

    if marker_pattern.search(original):
        updated = marker_pattern.sub("", original).rstrip()
        if updated:
            updated += "\n\n"
        updated += desired_block + "\n"
    else:
        updated = original
        legacy = bootstrap.strip()
        legacy_section = re.compile(
            rf"\n*## Bibliotec Fleet Bootstrap\s*\n+{re.escape(legacy)}\s*",
            re.DOTALL,
        )
        updated = legacy_section.sub("\n", updated, count=1)
        if legacy in updated:
            updated = updated.replace(legacy, "", 1)
        updated = updated.rstrip()
        if updated:
            updated += "\n\n"
        updated += desired_block + "\n"

    if updated == original:
        return False
    if not dry_run:
        soul_path.parent.mkdir(parents=True, exist_ok=True)
        soul_path.write_text(updated)
    return True


def plan_external_dir_update(current: object, target: str) -> list[str] | None:
    """Return a safe ``hermes config`` argument tail, or None when configured."""
    target = str(expand(target))
    if current is None or current == "":
        # Hermes accepts one external directory as a scalar and normalizes it at runtime.
        return ["set", "skills.external_dirs", target]
    if isinstance(current, str):
        if str(expand(current)) == target:
            return None
        raise OnboardingError(
            "skills.external_dirs contains a different scalar path; refusing to overwrite it. "
            "Convert the setting to a YAML list with a supported config editor, then rerun."
        )
    if isinstance(current, list):
        if not current:
            return ["set", "skills.external_dirs", target]
        normalized = [str(expand(item)) for item in current]
        if target in normalized:
            return None
        return ["set", f"skills.external_dirs.{len(current)}", target]
    raise OnboardingError(
        f"skills.external_dirs has unsupported type {type(current).__name__}; refusing to modify it"
    )


def parse_config_value(text: str) -> object:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return stripped


def require_smoke_model(smoke_model: str | None) -> str:
    if smoke_model is None or not smoke_model.strip():
        raise OnboardingError(
            "smoke test requires --smoke-model provider/model for the playbook's cheap/iteration tier"
        )
    return smoke_model.strip()


def _compact_segment(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _provider_segment(provider: str) -> str:
    provider = provider.strip().lower()
    if provider.endswith("-codex"):
        return "codex"
    if provider.endswith("-coding"):
        return provider.split("-", 1)[0]
    return _compact_segment(provider)


def smoke_worker_name(model_ref: str, suffix: str, role: str = "wrk") -> str:
    if "/" not in model_ref:
        raise OnboardingError(f"smoke model must be provider/model, got {model_ref!r}")
    provider, model = model_ref.split("/", 1)
    provider_tag = _provider_segment(provider)
    model_tag = _compact_segment(model)
    budget = 32 - len(role) - len(provider_tag) - len(suffix) - 3
    if budget < 1:
        raise OnboardingError(f"smoke worker name budget exhausted for {model_ref!r}")
    model_tag = model_tag[:budget]
    if not model_tag:
        raise OnboardingError(f"smoke model {model_ref!r} does not yield a usable worker name")
    return f"{role}-{model_tag}-{provider_tag}-{suffix}"


def hermes_env(hermes_home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HERMES_HOME"] = str(hermes_home)
    return env


def configure_external_dir(
    checkout: Path,
    hermes_home: Path,
    *,
    runner: Runner = run_command,
    dry_run: bool = False,
) -> bool:
    env = hermes_env(hermes_home)
    current_result = require_ok(
        runner(
            ["hermes", "config", "get", "skills.external_dirs", "--json"],
            timeout=30,
            env=env,
        ),
        "read skills.external_dirs",
    )
    current = parse_config_value(current_result.stdout)
    action = plan_external_dir_update(current, str(checkout))
    if action is None:
        return False
    if not dry_run:
        require_ok(
            runner(["hermes", "config", *action], timeout=30, env=env),
            "configure skills.external_dirs",
        )
    return True


def update_checkout(checkout: Path, *, runner: Runner = run_command) -> None:
    status = require_ok(
        runner(["git", "-C", str(checkout), "status", "--porcelain"], timeout=30),
        "inspect bibliotec checkout",
    )
    if status.stdout.strip():
        raise OnboardingError(
            f"bibliotec checkout has uncommitted changes at {checkout}; refusing to update it"
        )
    branch = require_ok(
        runner(["git", "-C", str(checkout), "branch", "--show-current"], timeout=30),
        "inspect bibliotec branch",
    ).stdout.strip()
    if branch != "main":
        raise OnboardingError(
            f"bibliotec checkout is on branch {branch or '<detached>'}; refusing to switch branches"
        )
    require_ok(
        runner(["git", "-C", str(checkout), "fetch", "--prune", "origin"], timeout=120),
        "fetch bibliotec",
    )
    require_ok(
        runner(
            ["git", "-C", str(checkout), "pull", "--ff-only", "origin", "main"],
            timeout=120,
        ),
        "fast-forward bibliotec",
    )


def ensure_checkout(
    checkout: Path,
    repo_url: str,
    *,
    runner: Runner = run_command,
    skip_update: bool = False,
    dry_run: bool = False,
) -> str:
    git_dir = checkout / ".git"
    if git_dir.is_dir():
        if skip_update or dry_run:
            return "unchanged"
        update_checkout(checkout, runner=runner)
        return "updated"
    if checkout.exists() and any(checkout.iterdir()):
        raise OnboardingError(f"checkout destination exists and is not empty: {checkout}")
    if dry_run:
        return "would-clone"
    checkout.parent.mkdir(parents=True, exist_ok=True)
    require_ok(
        runner(["git", "clone", repo_url, str(checkout)], timeout=300),
        "clone bibliotec",
    )
    return "cloned"


def check_commands(*, smoke_test: bool) -> list[str]:
    missing_required = [name for name in REQUIRED_COMMANDS if shutil.which(name) is None]
    if smoke_test:
        missing_required.extend(
            name for name in ("herdr", "pi") if shutil.which(name) is None
        )
    if missing_required:
        raise OnboardingError("missing required commands: " + ", ".join(sorted(set(missing_required))))
    return [name for name in RECOMMENDED_COMMANDS if shutil.which(name) is None]


def _json_result(result: CommandResult, action: str) -> dict:
    require_ok(result, action)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise OnboardingError(f"{action} returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise OnboardingError(f"{action} returned unexpected JSON")
    return payload


def _wait_for_shell(pane_id: str, runner: Runner, *, attempts: int = 180) -> None:
    for _ in range(attempts):
        result = runner(["herdr", "pane", "process-info", "--pane", pane_id], timeout=10)
        if result.returncode == 0:
            try:
                payload = json.loads(result.stdout)
            except json.JSONDecodeError:
                payload = {}
            info = payload.get("result", {}).get("process_info", {}) if isinstance(payload, dict) else {}
            foreground = info.get("foreground_processes") if isinstance(info, dict) else None
            shell_pid = info.get("shell_pid") if isinstance(info, dict) else None
            if (
                isinstance(foreground, list)
                and len(foreground) == 1
                and isinstance(foreground[0], dict)
                and shell_pid is not None
                and foreground[0].get("pid") == shell_pid
            ):
                time.sleep(1)
                return
        time.sleep(0.2)
    raise OnboardingError(f"shell did not become ready in pane {pane_id}")


def run_herdr_smoke(
    *,
    checkout: Path,
    hermes_home: Path,
    model: str,
    runner: Runner = run_command,
) -> Path:
    if os.environ.get("HERDR_ENV") != "1":
        raise OnboardingError("smoke test requires running inside a Herdr-managed pane (HERDR_ENV=1)")
    role = checkout / "agents" / "workhorse.md"
    if not role.is_file():
        raise OnboardingError(f"workhorse role is missing: {role}")

    run_id = uuid.uuid4().hex[:8]
    smoke_dir = hermes_home / "tmp" / f"bibliotec-onboarding-{run_id}"
    artifact = hermes_home / "artifacts" / f"bibliotec-onboarding-smoke-{run_id}.md"
    smoke_dir.mkdir(parents=True, exist_ok=True)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    (smoke_dir / "README.md").write_text(
        "# Bibliotec Hermes onboarding smoke fixture\n\n"
        "This fixture proves a bibliotec role can be loaded by a Herdr/Pi worker.\n"
    )

    pane_id: str | None = None
    try:
        split = _json_result(
            runner(
                [
                    "herdr",
                    "pane",
                    "split",
                    "--current",
                    "--direction",
                    "down",
                    "--cwd",
                    str(smoke_dir),
                    "--no-focus",
                ],
                timeout=30,
            ),
            "split smoke pane",
        )
        try:
            pane_id = split["result"]["pane"]["pane_id"]
        except (KeyError, TypeError) as exc:
            raise OnboardingError("split smoke pane did not return a pane_id") from exc

        _wait_for_shell(pane_id, runner)
        agent_name = smoke_worker_name(model, run_id[:4])
        _json_result(
            runner(
                [
                    "herdr",
                    "agent",
                    "start",
                    agent_name,
                    "--kind",
                    "pi",
                    "--pane",
                    pane_id,
                    "--timeout",
                    "60000",
                    "--",
                    "--model",
                    model,
                ],
                timeout=90,
            ),
            "start smoke worker",
        )
        prompt = (
            f"Read {role} and follow that role. Read README.md in the current directory, then "
            f"write {artifact} with a one-sentence grounded summary and end it with exactly "
            "'DONE: workhorse | bibliotec Hermes onboarding smoke test passed'. "
            "Do not modify any other file. Write the artifact before replying."
        )
        require_ok(
            runner(
                [
                    "herdr",
                    "agent",
                    "prompt",
                    agent_name,
                    prompt,
                    "--wait",
                    "--timeout",
                    "180000",
                ],
                timeout=210,
            ),
            "run smoke worker prompt",
        )
        if not artifact.is_file():
            raise OnboardingError("smoke worker settled without writing the artifact")
        receipt = "DONE: workhorse | bibliotec Hermes onboarding smoke test passed"
        if receipt not in artifact.read_text():
            raise OnboardingError("smoke artifact is missing the expected DONE receipt")
        return artifact
    finally:
        if pane_id is not None:
            runner(["herdr", "pane", "close", pane_id], timeout=30)


def _parse_skill_names(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped.startswith("│"):
            continue
        cells = [cell.strip() for cell in line.split("│")]
        if len(cells) < 3:
            continue
        name = cells[1].rstrip("…")
        if name and name != "Name":
            names.add(name)
    return names


def verify_installation(
    checkout: Path,
    hermes_home: Path,
    *,
    runner: Runner = run_command,
) -> list[str]:
    env = hermes_env(hermes_home)
    config = require_ok(
        runner(["hermes", "config", "get", "skills.external_dirs", "--json"], timeout=30, env=env),
        "read skills.external_dirs",
    )
    current = parse_config_value(config.stdout)
    normalized = [current] if isinstance(current, str) else current
    if not isinstance(normalized, list) or str(checkout) not in [str(expand(item)) for item in normalized]:
        raise OnboardingError("bibliotec checkout is not present in skills.external_dirs")

    require_ok(runner(["hermes", "config", "check"], timeout=120, env=env), "validate Hermes config")
    skills = require_ok(
        runner(["hermes", "skills", "list", "--source", "local", "--enabled-only"], timeout=120, env=env),
        "list Hermes skills",
    )
    discovered = _parse_skill_names(skills.stdout)
    found = [name for name in REQUIRED_SKILLS if name in discovered]
    missing = sorted(set(REQUIRED_SKILLS) - set(found))
    if missing:
        raise OnboardingError("Hermes did not discover required bibliotec skills: " + ", ".join(missing))
    return found


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", default=str(DEFAULT_CHECKOUT), help="bibliotec checkout path")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL)
    parser.add_argument("--hermes-home", default=os.environ.get("HERMES_HOME", "~/.hermes"))
    parser.add_argument("--skip-update", action="store_true", help="do not pull an existing checkout")
    parser.add_argument("--verify-only", action="store_true", help="make no changes; verify the existing integration")
    parser.add_argument("--dry-run", action="store_true", help="report intended changes without writing")
    parser.add_argument("--smoke-test", action="store_true", help="run a fresh Herdr/Pi workhorse smoke test")
    parser.add_argument(
        "--smoke-model",
        help="provider/model for the playbook's cheap/iteration tier on this node",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    checkout = expand(args.checkout)
    hermes_home = expand(args.hermes_home)
    report = Report(checkout=str(checkout), hermes_home=str(hermes_home))
    try:
        report.missing_recommended_commands = check_commands(smoke_test=args.smoke_test)
        if not args.verify_only:
            report.checkout_action = ensure_checkout(
                checkout,
                args.repo_url,
                skip_update=args.skip_update,
                dry_run=args.dry_run,
            )
            bootstrap_path = checkout / "prompts" / "fleet-bootstrap.md"
            if not bootstrap_path.is_file():
                raise OnboardingError(f"fleet bootstrap is missing: {bootstrap_path}")
            report.config_action = (
                "updated"
                if configure_external_dir(
                    checkout, hermes_home, dry_run=args.dry_run
                )
                else "unchanged"
            )
            report.bootstrap_action = (
                "updated"
                if upsert_bootstrap(
                    hermes_home / "SOUL.md",
                    extract_bootstrap_stanza(bootstrap_path.read_text()),
                    dry_run=args.dry_run,
                )
                else "unchanged"
            )
        if not args.dry_run:
            report.skills_verified = verify_installation(checkout, hermes_home)
            if args.smoke_test:
                report.smoke_artifact = str(
                    run_herdr_smoke(
                        checkout=checkout,
                        hermes_home=hermes_home,
                        model=require_smoke_model(args.smoke_model),
                    )
                )
    except OnboardingError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc), "report": asdict(report)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    payload = {"ok": True, "report": asdict(report)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Hermes onboarding complete")
        print(json.dumps(payload["report"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
