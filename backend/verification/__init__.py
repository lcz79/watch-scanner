# verification package — sistema di verifica autenticità orologi di lusso
from verification.rules_db import AUTHENTICATION_RULES, get_rules_for_model
from verification.serial_validator import validate_serial, SerialValidationResult
from verification.known_fakes import KNOWN_FAKE_PATTERNS, find_matching_fakes
from verification.report import generate_report, AuthenticityReport

__all__ = [
    "AUTHENTICATION_RULES",
    "get_rules_for_model",
    "validate_serial",
    "SerialValidationResult",
    "KNOWN_FAKE_PATTERNS",
    "find_matching_fakes",
    "generate_report",
    "AuthenticityReport",
]
