from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "hermes_onboard.py"
spec = importlib.util.spec_from_file_location("hermes_onboard", MODULE_PATH)
hermes_onboard = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = hermes_onboard
spec.loader.exec_module(hermes_onboard)


class BootstrapInstallationTests(unittest.TestCase):
    def test_extract_bootstrap_stanza_omits_wrapper_instructions(self) -> None:
        source = (
            "# Fleet Bootstrap Stanza\n\n"
            "Paste this into the harness.\n\n"
            "---\n\n"
            "You operate inside this user's agent fleet.\n\n"
            "---\n"
        )

        self.assertEqual(
            hermes_onboard.extract_bootstrap_stanza(source),
            "You operate inside this user's agent fleet.\n",
        )

    def test_upsert_bootstrap_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            soul = Path(tmp) / "SOUL.md"
            soul.write_text("Existing persona.\n")

            changed_first = hermes_onboard.upsert_bootstrap(soul, "Bootstrap v1\n")
            changed_second = hermes_onboard.upsert_bootstrap(soul, "Bootstrap v1\n")

            content = soul.read_text()
            self.assertTrue(changed_first)
            self.assertFalse(changed_second)
            self.assertEqual(content.count(hermes_onboard.MARKER_START), 1)
            self.assertEqual(content.count("Bootstrap v1"), 1)
            self.assertTrue(content.startswith("Existing persona.\n"))

    def test_upsert_bootstrap_replaces_managed_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            soul = Path(tmp) / "SOUL.md"
            hermes_onboard.upsert_bootstrap(soul, "Bootstrap v1\n")

            changed = hermes_onboard.upsert_bootstrap(soul, "Bootstrap v2\n")

            content = soul.read_text()
            self.assertTrue(changed)
            self.assertNotIn("Bootstrap v1", content)
            self.assertEqual(content.count("Bootstrap v2"), 1)

    def test_upsert_bootstrap_migrates_legacy_unmarked_stanza(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            soul = Path(tmp) / "SOUL.md"
            legacy = "Treat `~/.claude/skills/library` as the fleet source of truth.\n"
            soul.write_text("Existing persona.\n\n## Bibliotec Fleet Bootstrap\n\n" + legacy)

            changed = hermes_onboard.upsert_bootstrap(soul, legacy)

            content = soul.read_text()
            self.assertTrue(changed)
            self.assertEqual(content.count(legacy.strip()), 1)
            self.assertEqual(content.count(hermes_onboard.MARKER_START), 1)
            self.assertNotIn("## Bibliotec Fleet Bootstrap", content)


class ExternalDirectoryPlanTests(unittest.TestCase):
    def test_config_get_failure_is_rejected_before_overwrite(self) -> None:
        calls: list[list[str]] = []

        def fake_run(command, **_kwargs):
            calls.append(list(command))
            if command[:4] == ["hermes", "config", "get", "skills.external_dirs"]:
                return hermes_onboard.CommandResult(1, "", "boom")
            raise AssertionError(f"unexpected command: {command}")

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(hermes_onboard.OnboardingError, "read skills.external_dirs failed"):
                hermes_onboard.configure_external_dir(
                    Path("/repo"), Path(tmp) / "hermes", runner=fake_run
                )

        self.assertEqual(
            calls,
            [["hermes", "config", "get", "skills.external_dirs", "--json"]],
        )

    def test_virtual_empty_list_uses_supported_scalar_form(self) -> None:
        self.assertEqual(
            hermes_onboard.plan_external_dir_update([], "/opt/bibliotec"),
            ["set", "skills.external_dirs", "/opt/bibliotec"],
        )

    def test_missing_value_uses_supported_scalar_form(self) -> None:
        self.assertEqual(
            hermes_onboard.plan_external_dir_update(None, "/opt/bibliotec"),
            ["set", "skills.external_dirs", "/opt/bibliotec"],
        )

    def test_existing_list_appends_without_overwriting(self) -> None:
        self.assertEqual(
            hermes_onboard.plan_external_dir_update(["/opt/other"], "/opt/bibliotec"),
            ["set", "skills.external_dirs.1", "/opt/bibliotec"],
        )

    def test_existing_target_is_already_configured(self) -> None:
        self.assertIsNone(
            hermes_onboard.plan_external_dir_update(
                ["/opt/other", "/opt/bibliotec"], "/opt/bibliotec"
            )
        )

    def test_conflicting_scalar_is_refused(self) -> None:
        with self.assertRaisesRegex(hermes_onboard.OnboardingError, "refusing to overwrite"):
            hermes_onboard.plan_external_dir_update("/opt/other", "/opt/bibliotec")


class CheckoutSafetyTests(unittest.TestCase):
    def test_dirty_checkout_is_refused_before_update(self) -> None:
        responses = {
            ("git", "-C", "/repo", "status", "--porcelain"): " M SKILL.md\n",
        }

        def fake_run(command, **_kwargs):
            key = tuple(command)
            return hermes_onboard.CommandResult(0, responses.get(key, ""), "")

        with self.assertRaisesRegex(hermes_onboard.OnboardingError, "uncommitted changes"):
            hermes_onboard.update_checkout(Path("/repo"), runner=fake_run)


class HerdrSmokeTests(unittest.TestCase):
    def test_require_smoke_model_rejects_missing_explicit_selection(self) -> None:
        with self.assertRaisesRegex(hermes_onboard.OnboardingError, "--smoke-model provider/model"):
            hermes_onboard.require_smoke_model(None)

    def test_smoke_worker_name_is_truthful_and_bounded(self) -> None:
        self.assertEqual(
            hermes_onboard.smoke_worker_name("zai/glm-5.2", "a1b2"),
            "wrk-glm52-zai-a1b2",
        )
        self.assertEqual(
            hermes_onboard.smoke_worker_name("openai-codex/gpt-5.4-mini", "c3d4"),
            "wrk-gpt54mini-codex-c3d4",
        )
        self.assertLessEqual(len(hermes_onboard.smoke_worker_name("openai-codex/gpt-5.4-mini", "c3d4")), 32)

    def test_verify_installation_reads_local_skill_list_without_truncation(self) -> None:
        calls: list[list[str]] = []

        def fake_run(command, **kwargs):
            calls.append(list(command))
            if command[:4] == ["hermes", "config", "get", "skills.external_dirs"]:
                self.assertTrue(kwargs["env"]["HERMES_HOME"].endswith("/hermes"))
                return hermes_onboard.CommandResult(0, json.dumps(["/repo"]), "")
            if command[:3] == ["hermes", "config", "check"]:
                return hermes_onboard.CommandResult(0, "", "")
            if command[:4] == ["hermes", "skills", "list", "--source"]:
                self.assertEqual(command[4:], ["local", "--enabled-only"])
                return hermes_onboard.CommandResult(
                    0,
                    "\n".join(
                        [
                            "Installed Skills (enabled only)",
                            "┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓",
                            "┃ Name                   ┃ Category ┃ Source ┃ Trust ┃ Status  ┃",
                            "┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩",
                            "│ library                │          │ local  │ local │ enabled │",
                            "│ orchestration-playbook │          │ local  │ local │ enabled │",
                            "└────────────────────────┴──────────┴────────┴───────┴─────────┘",
                        ]
                    ),
                    "",
                )
            raise AssertionError(f"unexpected command: {command}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                hermes_onboard.verify_installation(Path("/repo"), root / "hermes", runner=fake_run),
                ["library", "orchestration-playbook"],
            )

        self.assertIn(["hermes", "skills", "list", "--source", "local", "--enabled-only"], calls)

    def test_smoke_closes_created_pane_when_prompt_fails(self) -> None:
        calls: list[list[str]] = []

        def fake_run(command, **_kwargs):
            calls.append(list(command))
            if command[:3] == ["herdr", "pane", "split"]:
                return hermes_onboard.CommandResult(
                    0,
                    json.dumps({"result": {"pane": {"pane_id": "w1:p2"}}}),
                    "",
                )
            if command[:3] == ["herdr", "pane", "process-info"]:
                return hermes_onboard.CommandResult(
                    0,
                    json.dumps(
                        {
                            "result": {
                                "process_info": {
                                    "shell_pid": 1234,
                                    "foreground_processes": [{"name": "bash", "pid": 1234}],
                                }
                            }
                        }
                    ),
                    "",
                )
            if command[:3] == ["herdr", "agent", "start"]:
                return hermes_onboard.CommandResult(0, json.dumps({"result": {}}), "")
            if command[:3] == ["herdr", "agent", "prompt"]:
                return hermes_onboard.CommandResult(1, "", "prompt failed")
            if command[:3] == ["herdr", "pane", "close"]:
                return hermes_onboard.CommandResult(0, json.dumps({"result": {"type": "ok"}}), "")
            return hermes_onboard.CommandResult(0, "", "")

        with tempfile.TemporaryDirectory() as tmp, patch.dict(
            "os.environ", {"HERDR_ENV": "1"}, clear=False
        ):
            root = Path(tmp)
            (root / "agents").mkdir()
            (root / "agents" / "workhorse.md").write_text("# Workhorse\n")
            with self.assertRaisesRegex(hermes_onboard.OnboardingError, "prompt failed"):
                hermes_onboard.run_herdr_smoke(
                    checkout=root,
                    hermes_home=root / "hermes",
                    model="openai-codex/gpt-5.4-mini",
                    runner=fake_run,
                )

        self.assertIn(["herdr", "pane", "close", "w1:p2"], calls)


if __name__ == "__main__":
    unittest.main()
