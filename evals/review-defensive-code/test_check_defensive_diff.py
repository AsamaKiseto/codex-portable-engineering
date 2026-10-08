"""在临时 Git 仓库中验证退出状态、增量范围和只读行为。"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "skills" / "review-defensive-code" / "scripts" / "check_defensive_diff.py"
SWALLOW = "try:\n    work()\nexcept Exception:\n    pass\n"
FALLBACK = "value = config.get('width', 32)\n"


class DiffChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "skill-test@example.invalid")
        self.git("config", "user.name", "Skill test")
        self.write("stable.py", "value = 1\n")
        self.commit()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout

    def write(self, path, source):
        target = self.repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")

    def commit(self):
        self.git("add", ".")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD").decode().strip()

    def check(self, *args):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo), "--format", "json", *args],
            capture_output=True, text=True,
        )
        return result.returncode, json.loads(result.stdout)

    def test_new_swallow_blocks_and_leaves_worktree_and_index_unchanged(self):
        self.write("new.py", SWALLOW)
        before = self.git("status", "--porcelain=v1", "-z")
        index = self.git("ls-files", "--stage", "-z")
        code, report = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(self.git("status", "--porcelain=v1", "-z"), before)
        self.assertEqual(self.git("ls-files", "--stage", "-z"), index)
        self.assertEqual((self.repo / "new.py").read_text(), SWALLOW)

    def test_expected_exception_is_allowed_and_fallback_needs_review(self):
        self.write("new.py", "try:\n    work()\nexcept FileNotFoundError:\n    pass\n")
        self.assertEqual(self.check()[0], 0)
        self.write("new.py", FALLBACK)
        code, report = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "needs_review")
        self.assertEqual(self.check("--fail-on-review")[0], 1)

    def test_validation_and_algorithm_are_candidates_not_hard_failures(self):
        self.write("new.py", "if width < 1:\n    raise ValueError(width)\ny = x.clamp(0, 1)\n")
        code, report = self.check()
        self.assertEqual(code, 0)
        self.assertEqual({item["rule"] for item in report["findings"]}, {"D101", "D104"})

    def test_existing_guard_body_and_line_changes_do_not_reflag(self):
        self.write("old.py", "if size < 1:\n    raise ValueError('size')\n" + SWALLOW)
        self.commit()
        self.write("old.py", "# new comment\n\nif size < 1:\n    raise ValueError('bad size')\n" + SWALLOW)
        code, report = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(report["findings"], [])

    def test_duplicate_new_occurrence_is_reported(self):
        self.write("old.py", SWALLOW)
        self.commit()
        self.write("old.py", SWALLOW + SWALLOW)
        code, report = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(len(report["findings"]), 1)

    def test_rename_and_added_guard(self):
        self.write("old.py", SWALLOW + "\n".join(f"value_{n} = {n}" for n in range(25)) + "\n")
        self.commit()
        self.git("mv", "old.py", "带 空格.py")
        self.assertEqual(self.check()[1]["findings"], [])
        with (self.repo / "带 空格.py").open("a") as stream:
            stream.write(FALLBACK)
        code, report = self.check("--path", "带 空格.py")
        self.assertEqual(code, 0)
        self.assertEqual([item["rule"] for item in report["findings"]], ["D102"])

    def test_staged_mode_uses_index_snapshot(self):
        self.write("stable.py", SWALLOW)
        self.git("add", "stable.py")
        self.write("stable.py", "value = 1\n")
        self.assertEqual(self.check()[0], 0)
        self.assertEqual(self.check("--staged")[0], 1)

    def test_commit_comparison_ignores_dirty_worktree(self):
        base = self.git("rev-parse", "HEAD").decode().strip()
        self.write("stable.py", SWALLOW)
        head = self.commit()
        self.write("stable.py", "value = 1\n")
        self.assertEqual(self.check("--base", base, "--head", head)[0], 1)
        self.assertEqual(self.check("--base", base)[0], 0)

    def test_scope_ignored_files_and_unusual_names(self):
        self.write(".gitignore", "ignored/\n")
        self.write("ignored/new.py", SWALLOW)
        self.write("other/new.py", SWALLOW)
        self.write("owned/line\nbreak.py", FALLBACK)
        code, report = self.check("--path", "owned")
        self.assertEqual(code, 0)
        self.assertEqual(report["scanned_python"], ["owned/line\nbreak.py"])
        self.assertNotIn("ignored/new.py", self.check()[1]["scanned_python"])

    def test_syntax_and_git_errors_are_incomplete(self):
        self.write("bad.py", "if\n")
        code, report = self.check()
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(self.check("--base", "missing-ref")[0], 2)

    def test_non_python_and_symlinks_are_reported_as_unscanned(self):
        self.write("client.js", "try { run(); } catch (error) {}\n")
        os.symlink("stable.py", self.repo / "linked.py")
        code, report = self.check()
        self.assertEqual(code, 0)
        self.assertEqual(set(report["unscanned"]), {"client.js", "linked.py"})
        self.assertTrue(report["semantic_review_required"])

    def test_comments_and_strings_do_not_trigger(self):
        self.write("text.py", "# except Exception: pass\nexample = 'x.clamp(0, 1)'\n")
        self.assertEqual(self.check()[1]["findings"], [])

    def test_pep263_source_is_supported(self):
        (self.repo / "latin.py").write_bytes(("# coding: latin-1\n# caf\xe9\n" + FALLBACK).encode("latin-1"))
        self.assertEqual(self.check()[1]["status"], "needs_review")

    def test_wide_catch_with_return_is_reviewed(self):
        self.write("new.py", "def run():\n    try:\n        work()\n    except BaseException:\n        return None\n")
        code, report = self.check()
        self.assertEqual(code, 0)
        self.assertEqual([item["rule"] for item in report["findings"]], ["D103"])

    def test_bare_and_tuple_swallow_are_blocked(self):
        for clause in ("except:", "except (ValueError, Exception):", "except builtins.Exception:"):
            with self.subTest(clause=clause):
                self.write("new.py", f"try:\n    work()\n{clause}\n    pass\n")
                self.assertEqual(self.check()[0], 1)

    def test_deletion_does_not_reflag_removed_code(self):
        self.write("old.py", SWALLOW)
        self.commit()
        (self.repo / "old.py").unlink()
        self.assertEqual(self.check()[1]["findings"], [])


if __name__ == "__main__":
    unittest.main()
