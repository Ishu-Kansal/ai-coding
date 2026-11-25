class CapturingLogger:
    def __init__(self):
        # Store log events in a format that tests can assert without a real logger.
        self.lines = []

    def info(self, message):
        # Record informational pipeline milestones with their severity.
        self.lines.append("INFO: " + message)

    def error(self, message):
        # Record failed pipeline stages distinctly so tests can verify error paths.
        self.lines.append("ERROR: " + message)

    def get_logs(self):
        # Expose the captured ordered log stream for approval or direct assertions.
        return self.lines
