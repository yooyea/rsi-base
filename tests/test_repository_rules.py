import copy
import json
import unittest

from scripts.check_repository_rules import POLICY, validate_ruleset


class RepositoryRulesChecks(unittest.TestCase):
    def setUp(self):
        self.expected = json.loads(POLICY.read_text())
        self.actual = copy.deepcopy(self.expected)

    def status_parameters(self):
        return next(r["parameters"] for r in self.actual["rules"]
                    if r["type"] == "required_status_checks")

    def test_matching_policy_passes(self):
        self.assertEqual(validate_ruleset(self.actual, self.expected), [])

    def test_committed_policy_has_no_admin_bypass_and_requires_actions_check(self):
        self.assertEqual(self.expected["bypass_actors"], [])
        self.assertEqual(self.expected["enforcement"], "active")
        self.assertEqual(self.status_parameters()["required_status_checks"],
                         [{"context": "Documentation checks", "integration_id": 15368}])
        self.assertIs(self.status_parameters()["strict_required_status_checks_policy"], True)

    def test_server_metadata_and_rule_order_do_not_cause_false_failure(self):
        self.actual["id"] = 42
        self.actual["rules"].reverse()
        self.assertEqual(validate_ruleset(self.actual, self.expected), [])

    def test_missing_required_check_fails(self):
        self.status_parameters()["required_status_checks"] = []
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_wrong_provider_fails(self):
        self.status_parameters()["required_status_checks"][0]["integration_id"] = 99
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_stale_base_allowed_fails(self):
        self.status_parameters()["strict_required_status_checks_policy"] = False
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_disabled_rules_fails(self):
        self.actual["enforcement"] = "disabled"
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_bypass_actor_fails(self):
        self.actual["bypass_actors"] = [{"actor_type": "RepositoryRole", "actor_id": 5,
                                         "bypass_mode": "always"}]
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_unreadable_bypass_list_is_not_assumed_empty(self):
        del self.actual["bypass_actors"]
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_excluded_main_fails(self):
        self.actual["conditions"]["ref_name"]["exclude"] = ["refs/heads/main"]
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_missing_pr_requirement_fails(self):
        self.actual["rules"] = [r for r in self.actual["rules"] if r["type"] != "pull_request"]
        self.assertTrue(validate_ruleset(self.actual, self.expected))

    def test_wrong_json_type_is_not_equivalent(self):
        self.status_parameters()["strict_required_status_checks_policy"] = 1
        self.assertTrue(validate_ruleset(self.actual, self.expected))


if __name__ == "__main__":
    unittest.main()
