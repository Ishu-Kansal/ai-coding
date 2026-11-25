class Pipeline:
    def __init__(self, config, emailer, log):
        # Keep infrastructure dependencies injected so pipeline decisions remain
        # independent of the concrete configuration, email, and logging services.
        self.config = config
        self.emailer = emailer
        self.log = log

    def run(self, project, MAX_DEPLOY):
        # The pipeline has two success gates: tests must pass before deployment,
        # and deployment is only attempted when those tests have succeeded.
        tests_passed = False
        deploy_successful = False

        if project.has_tests():
            # Projects with tests require an explicit successful test run; any
            # other status prevents deployment because untested code is unsafe.
            if "success" == project.run_tests():
                self.log.info("Tests passed")
                tests_passed = True
            else:
                self.log.error("Tests failed")
                tests_passed = False
        else:
            # An explicitly testless project is not a test failure: it may proceed
            # directly to deployment, so preserve the successful-test gate.
            self.log.info("No tests")
            tests_passed = True

        deploy_successful = False
        if tests_passed:
            # MAX_DEPLOY is the total attempt limit, including the first
            # deployment; stop early as soon as one attempt succeeds.
            for _ in range(MAX_DEPLOY):
                deploy_successful = self.deploy_status(project, tests_passed)
                if deploy_successful:
                    break

        if self.config.send_email_summary():
            self.log.info("Sending email")
            if tests_passed:
                if deploy_successful:
                    # Both gates passed, so communicate a completed deployment.
                    self.emailer.send("Deployment completed successfully")
                else:
                    # Tests passed but deployment did not, isolating the failed stage.
                    self.emailer.send("Deployment failed")
            else:
                # The deployment was skipped because tests failed, so report the
                # earliest unsuccessful stage instead of deployment.
                self.emailer.send("Tests failed")
        else:
            # Summary delivery is optional; disabling it must not alter pipeline
            # execution or the test and deployment outcomes.
            self.log.info("Email disabled")

    def deploy_status(self, project, tests_passed):
        # Deployment is the second pipeline stage and runs only after the
        # test gate succeeds; a failed test gate bypasses deployment entirely.
        if not tests_passed:
            return False

        if "success" == project.deploy():
            self.log.info("Deployment successful")
            return True

        self.log.error("Deployment failed")
        return False
