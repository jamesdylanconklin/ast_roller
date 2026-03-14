"""
Skeleton tests for logging behavior.

These tests are intentionally left as scaffolding and should be completed
once the preferred logging invocation strategy is finalized.
"""

import logging
from pathlib import Path

import pytest
from logging_test_cases import ERROR_LOGGING_CASES, LOGGING_CASES, LoggingCase

from ast_roller.main import main


@pytest.fixture
def in_log_workspace(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(log_dir)  # auto-restored by pytest
    return log_dir


def generate_args(case: LoggingCase) -> list[str]:
    args = []
    if case.log_boolean:
        args.append("-l")
        if case.log_file is not None:
            args.extend(["--log-file", case.log_file])
    if case.description is not None:
        args.extend(["-d", case.description])
    args.append(case.roll_string)
    return args


def run_and_validate_log_event(
    case: LoggingCase,
    caplog: pytest.LogCaptureFixture,
):
    caplog.clear()
    caplog.set_level(logging.INFO, logger="ast_roller.main")

    args = generate_args(case)

    main(args)

    events = [
        record for record in caplog.records if record.name == "ast_roller.main" and record.levelno == logging.INFO
    ]

    if not case.log_boolean:
        assert not events, "Expected no INFO log events from ast_roller.main when logging is disabled"
        return None

    assert events, "Expected at least one INFO log event from ast_roller.main when logging is enabled"

    log_event = events[-1]
    expected_prefix = case.description if case.description is not None else "*"
    assert log_event.getMessage().startswith(f"{expected_prefix}:"), log_event.getMessage()

    return log_event


def validate_log_file(
    case: LoggingCase,
):
    # Check for log file if relevant
    if case.log_boolean and case.log_file is not None:
        expected_log_path = Path.cwd() / case.log_file
        assert expected_log_path.exists(), f"Expected log file {expected_log_path} does not exist."
        with open(case.log_file) as f:
            log_contents = f.read()
            expected_prefix = case.description if case.description is not None else "*"
            assert log_contents.startswith(f"{expected_prefix}:"), (
                f"Log file {case.log_file} does not start with expected prefix. Contents: {log_contents}"
            )

    return


class TestLogging:
    @pytest.mark.parametrize("case", LOGGING_CASES, ids=[case.name for case in LOGGING_CASES])
    def test_log_destination_and_description(self, case, in_log_workspace, caplog):
        run_and_validate_log_event(case, caplog)
        validate_log_file(case)

    @pytest.mark.parametrize("case", ERROR_LOGGING_CASES, ids=[case.name for case in ERROR_LOGGING_CASES])
    def test_logging_errors(self, case, capsys, in_log_workspace):
        with pytest.raises(SystemExit, match="1"):
            main(generate_args(case))

        captured = capsys.readouterr()
        assert case.reason in captured.err
