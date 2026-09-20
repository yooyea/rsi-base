from pathlib import Path
import tempfile
import unittest

from scripts.check_docs import HEADINGS, validate


class DocumentationChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("README.md", "# Purpose\n\n[Entry](SKILL.md)\n")
        self.write("AGENTS.md", "# Work\n")
        self.write("SKILL.md", "---\nname: rsi-base\ndescription: Guidance\n---\n\n# Entry\n")
        self.rule = "chapters/engineering/rules/test/example.md"
        with (self.root / "SKILL.md").open("a") as entry:
            entry.write(f"\n[Rule]({self.rule})\n")
        self.write(self.rule, "# Rule\n\n" + "\n\n".join(f"## {h}\n\nContent" for h in HEADINGS))

    def write(self, name: str, text: str):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_valid_repository_passes(self):
        self.assertEqual(validate(self.root), [])

    def test_broken_link_fails_then_fixed_link_passes(self):
        self.write("README.md", "# Purpose\n\n[Entry](missing.md)\n")
        self.assertTrue(any("missing local target" in item for item in validate(self.root)))
        self.write("README.md", "# Purpose\n\n[Entry](SKILL.md)\n")
        self.assertEqual(validate(self.root), [])

    def test_missing_entry_fails(self):
        (self.root / "AGENTS.md").unlink()
        self.assertIn("Missing entry document: AGENTS.md", validate(self.root))

    def test_missing_frontmatter_fails(self):
        self.write("SKILL.md", "# Entry\n")
        self.assertIn("SKILL.md: missing frontmatter", validate(self.root))

    def test_missing_description_fails(self):
        self.write("SKILL.md", "---\nname: rsi-base\ndescription: \n---\n# Entry\n")
        self.assertIn("SKILL.md: missing description", validate(self.root))

    def test_rule_missing_section_fails(self):
        self.write(self.rule, "# Rule\n\n## 保障目标\n\nContent\n")
        self.assertTrue(any("missing section 工程落实" in item for item in validate(self.root)))

    def test_fenced_heading_does_not_satisfy_rule(self):
        text = (self.root / self.rule).read_text(encoding="utf-8")
        self.write(self.rule, text.replace("## 工程落实", "```md\n## 工程落实\n```"))
        self.assertTrue(any("missing section 工程落实" in item for item in validate(self.root)))

    def test_empty_section_fails(self):
        text = (self.root / self.rule).read_text()
        self.write(self.rule, text.replace("## 工程落实\n\nContent", "## 工程落实\n"))
        self.assertTrue(any("empty section 工程落实" in e for e in validate(self.root)))

    def test_unlinked_rule_fails_then_indexed_rule_passes(self):
        new_rule = "chapters/engineering/rules/test/new.md"
        self.write(new_rule, (self.root / self.rule).read_text())
        self.assertTrue(any("new.md: rule is not reachable" in e for e in validate(self.root)))
        with (self.root / self.rule).open("a") as entry:
            entry.write("\n[Next](new.md)\n")
        self.assertEqual(validate(self.root), [])

    def test_nested_rule_is_not_outside_coverage(self):
        self.write("chapters/engineering/rules/test/nested/new.md", "# Incomplete\n")
        errors = validate(self.root)
        self.assertTrue(any("nested/new.md: missing section" in e for e in errors))
        self.assertTrue(any("nested/new.md: rule is not reachable" in e for e in errors))

    def test_fenced_link_cannot_make_rule_reachable(self):
        self.write("SKILL.md", "---\nname: rsi-base\ndescription: Guidance\n---\n"
                   f"```md\n[Rule]({self.rule})\n```\n")
        self.assertTrue(any("not reachable" in e for e in validate(self.root)))

    def test_navigation_cycle_terminates(self):
        with (self.root / self.rule).open("a") as entry:
            entry.write("\n[Self](example.md)\n")
        self.assertEqual(validate(self.root), [])

    def test_nonclosing_fence_keeps_example_links_hidden(self):
        self.write("README.md", "# Purpose\n\n```md\n```not-a-closing-fence\n"
                   "[Example](missing.md)\n```\n")
        self.assertEqual(validate(self.root), [])

    def test_nonclosing_fence_cannot_satisfy_rule_heading(self):
        text = "# Rule\n\n" + "\n\n".join(
            f"## {h}\n\nContent" for h in HEADINGS if h != "工程落实"
        )
        text += "\n\n```md\n```not-a-closing-fence\n## 工程落实\n\nExample only\n```\n"
        self.write(self.rule, text)
        self.assertTrue(any("missing section 工程落实" in e for e in validate(self.root)))

    def test_four_space_pseudo_fence_does_not_hide_broken_link(self):
        self.write("README.md", "# Purpose\n\n    ```md\n\n[Broken](missing.md)\n")
        self.assertTrue(any("missing local target" in e for e in validate(self.root)))

    def test_four_space_pseudo_fence_does_not_hide_rule_headings(self):
        text = "# Rule\n\n    ```md\n\n" + "\n\n".join(
            f"## {h}\n\nContent" for h in HEADINGS
        )
        self.write(self.rule, text)
        self.assertEqual(validate(self.root), [])

    def test_four_space_delimiter_cannot_close_real_fence(self):
        self.write("README.md", "# Purpose\n\n```md\n    ```\n"
                   "[Example](missing.md)\n```\n")
        self.assertEqual(validate(self.root), [])

    def test_zero_to_three_space_fences_still_work(self):
        for indent in range(4):
            with self.subTest(indent=indent):
                padding = " " * indent
                self.write("README.md", f"# Purpose\n\n{padding}```md\n"
                           f"[Example](missing.md)\n{padding}``` \n")
                self.assertEqual(validate(self.root), [])

    def test_no_rules_fails(self):
        (self.root / self.rule).unlink()
        self.assertIn("No engineering rules found", validate(self.root))

    def test_empty_document_fails(self):
        self.write("extra.md", "  \n")
        self.assertTrue(any("empty document" in item for item in validate(self.root)))

    def test_links_cannot_escape_repository(self):
        self.write("README.md", "# Purpose\n\n[Outside](../../outside.md)\n")
        self.assertTrue(any("link escapes repository" in item for item in validate(self.root)))

    def test_examples_and_external_links_are_ignored(self):
        self.write("README.md", "# Purpose\n\n```md\n[Sample](missing.md)\n```\n"
                   "`[Inline](missing.md)`\n[External](https://example.invalid/not-checked)\n")
        self.assertEqual(validate(self.root), [])

    def test_symlink_escape_fails(self):
        with tempfile.TemporaryDirectory() as outside:
            destination = Path(outside) / "external.md"
            destination.write_text("# External\n", encoding="utf-8")
            (self.root / "escape.md").symlink_to(destination)
            self.assertTrue(any("document escapes repository" in item for item in validate(self.root)))


if __name__ == "__main__":
    unittest.main()
