from unittest.mock import Mock

import pytest

from build_pipeline.pipeline import Pipeline
from tests.capturing_logger import CapturingLogger


class TestPipeline:
    @staticmethod
    def create_pipeline():
        config = Mock()
        config.send_email_summary.return_value = False
        emailer = Mock()
        logger = CapturingLogger()
        return Pipeline(config, emailer, logger), emailer, logger

    def test_successful_test_status_allows_deployment(self):
        pipeline, emailer, logger = self.create_pipeline()
        project = Mock()
        project.has_tests.return_value = True
        project.run_tests.return_value = "success"
        project.deploy.return_value = "success"

        pipeline.run(project, MAX_DEPLOY=1)

        project.run_tests.assert_called_once_with()
        project.deploy.assert_called_once_with()
        assert logger.get_logs() == [
            "INFO: Tests passed",
            "INFO: Deployment successful",
            "INFO: Email disabled",
        ]
        emailer.send.assert_not_called()

    @pytest.mark.parametrize("deployment_status", ["failure", "error", "", "unexpected"])
    def test_non_success_deployment_status_marks_deployment_failed(
        self, deployment_status
    ):
        pipeline, emailer, logger = self.create_pipeline()
        project = Mock()
        project.has_tests.return_value = True
        project.run_tests.return_value = "success"
        project.deploy.return_value = deployment_status

        pipeline.run(project, MAX_DEPLOY=1)

        project.run_tests.assert_called_once_with()
        project.deploy.assert_called_once_with()
        assert logger.get_logs() == [
            "INFO: Tests passed",
            "ERROR: Deployment failed",
            "INFO: Email disabled",
        ]
        emailer.send.assert_not_called()

    def test_deployment_retries_until_success_or_attempt_limit(self):
        pipeline, _, _ = self.create_pipeline()
        project = Mock()
        project.has_tests.return_value = True
        project.run_tests.return_value = "success"
        project.deploy.side_effect = ["failure", "success", "failure"]

        pipeline.run(project, MAX_DEPLOY=3)

        assert project.deploy.call_count == 2

    def test_deployment_stops_after_maximum_attempts(self):
        pipeline, _, logger = self.create_pipeline()
        project = Mock()
        project.has_tests.return_value = True
        project.run_tests.return_value = "success"
        project.deploy.return_value = "failure"

        pipeline.run(project, MAX_DEPLOY=3)

        assert project.deploy.call_count == 3
        assert logger.get_logs().count("ERROR: Deployment failed") == 3

    @pytest.mark.parametrize(
        ("test_status", "deployment_statuses", "expected_email", "deploy_calls"),
        [
            ("success", ["success"], "Deployment completed successfully", 1),
            ("success", ["failure", "success"], "Deployment completed successfully", 2),
            ("success", ["failure", "failure", "failure"], "Deployment failed", 3),
            ("failure", [], "Tests failed", 0),
        ],
    )
    def test_sends_at_most_one_email_for_pipeline_outcome(
        self, test_status, deployment_statuses, expected_email, deploy_calls
    ):
        pipeline, emailer, _ = self.create_pipeline()
        pipeline.config.send_email_summary.return_value = True
        project = Mock()
        project.has_tests.return_value = True
        project.run_tests.return_value = test_status
        project.deploy.side_effect = deployment_statuses

        pipeline.run(project, MAX_DEPLOY=3)

        emailer.send.assert_called_once_with(expected_email)
        assert project.deploy.call_count == deploy_calls

    @pytest.mark.parametrize("test_status", ["failure", "error", "", "unexpected"])
    def test_non_success_test_status_marks_tests_failed_and_skips_deployment(
        self, test_status
    ):
        pipeline, emailer, logger = self.create_pipeline()
        project = Mock()
        project.has_tests.return_value = True
        project.run_tests.return_value = test_status

        pipeline.run(project, MAX_DEPLOY=3)

        project.run_tests.assert_called_once_with()
        project.deploy.assert_not_called()
        assert logger.get_logs() == [
            "ERROR: Tests failed",
            "INFO: Email disabled",
        ]
        emailer.send.assert_not_called()
