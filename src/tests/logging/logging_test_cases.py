"""
Test cases for CLI logging behavior.

The cases vary:
- explicit log file targets
- `None` for default log destination behavior
- explicit and unspecified descriptions for log line prefixes
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LoggingCase:
    name: str
    log_boolean: Optional[bool]
    log_file: Optional[str]
    description: Optional[str]
    roll_string: str
    reason: Optional[str] = None


ERROR_LOGGING_CASES = [
    LoggingCase(
      name="nonexistent_log_parent_directory",
      log_boolean=True,
      log_file="logs/combat.log",
      description="damage",
      roll_string="2d6+3",
      reason="Specified log file directory logs does not exist."
    ),    
]

LOGGING_CASES = [
    LoggingCase(
        name="explicit_file_with_description",
        log_boolean=True,
        log_file="rolls.log",
        description="initiative",
        roll_string="1d20",
    ),
    LoggingCase(
        name="explicit_file_unspecified_description",
        log_boolean=True,
        log_file="session.log",
        description=None,
        roll_string="4d6 dl1",
    ),
    LoggingCase(
        name="default_file_with_description",
        log_boolean=True,
        log_file=None,
        description="saving throw",
        roll_string="d20",
    ),
    LoggingCase(
        name="default_file_unspecified_description",
        log_boolean=False,
        log_file=None,
        description=None,
        roll_string="3d8",
    ),
        LoggingCase(
        name="logging_enabled_no_file_with_description",
        log_boolean=True,
        log_file=None,
        description=None,
        roll_string="3d8",
    ),
]
