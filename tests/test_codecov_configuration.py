import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class CodecovConfigurationTest(unittest.TestCase):
    def test_codecov_yaml_configuration(self):
        codecov_file = REPO_ROOT / "codecov.yml"
        self.assertTrue(codecov_file.is_file(), "codecov.yml must exist at repo root")
        content = codecov_file.read_text(encoding="utf-8")
        self.assertIn("coverage:", content)
        self.assertIn("flag_management:", content)
        self.assertIn("component_management:", content)
        self.assertIn("name: python", content)
        self.assertIn("component_id: python_code", content)

    def test_tests_workflow_codecov_step(self):
        tests_workflow = REPO_ROOT / ".github" / "workflows" / "tests.yml"
        self.assertTrue(
            tests_workflow.is_file(), ".github/workflows/tests.yml must exist"
        )
        content = tests_workflow.read_text(encoding="utf-8")
        self.assertIn("codecov/codecov-action", content)
        self.assertIn("CODECOV_TOKEN", content)
        self.assertIn("flags: python", content)
        self.assertIn("codecov.yml", content)

    def test_sonarcloud_configuration(self):
        sonar_file = REPO_ROOT / ".sonarcloud.properties"
        self.assertTrue(sonar_file.is_file(), ".sonarcloud.properties must exist")
        content = sonar_file.read_text(encoding="utf-8")
        self.assertIn("sonar.exclusions", content)
        self.assertIn("sonar.cpd.exclusions", content)
        self.assertIn(".github/**", content)
        self.assertIn("docs/**", content)


if __name__ == "__main__":
    unittest.main()
