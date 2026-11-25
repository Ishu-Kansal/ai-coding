from .status import NO_TESTS, PASSING_TESTS


class Project:
    @staticmethod
    def builder():
        # Provide one fluent entry point for creating test and deployment
        # configurations without exposing build-state details at call sites.
        return ProjectBuilder()

    def __init__(self, builds_successfully, test_status):
        # Represent the project's two relevant capabilities: whether deployment
        # can succeed and whether/how tests are configured.
        self.builds_successfully = builds_successfully
        self.test_status = test_status

    def has_tests(self):
        # NO_TESTS is the only test state that means the pipeline should skip
        # test execution; failing and passing statuses both represent test suites.
        return self.test_status != NO_TESTS

    def run_tests(self):
        # Translate the stored test status into the pipeline's success/failure
        # protocol; only PASSING_TESTS passes the test gate.
        return "success" if self.test_status == PASSING_TESTS else "failure"

    def deploy(self):
        # Translate the configured deployment capability into the pipeline's
        # success/failure protocol for a project build.
        return "success" if self.builds_successfully else "failure"


class ProjectBuilder:
    def __init__(self):
        # Start with conservative outcomes: no tests and deployment disabled.
        self.test_status = False
        self.builds_successfully = False

    def set_test_status(self, test_status):
        # Configure the project's test state, which controls whether tests run
        # and, for suites that exist, whether they pass or fail.
        self.test_status = test_status
        return self

    def set_deploys_successfully(self, builds_successfully):
        # Configure the simulated build/deployment outcome for the pipeline.
        self.builds_successfully = builds_successfully
        return self

    def build(self):
        # Freeze the configured test and deployment outcomes into a runnable
        # Project value; fluent setters can then be chained naturally.
        return Project(self.builds_successfully, self.test_status)
