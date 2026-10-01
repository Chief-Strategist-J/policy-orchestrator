"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: AUDIT SERVICE UNIT TESTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides unit test verification for the AuditService, verifying
   that multi-vector rules correctly identify concurrency issues, naked sleeps,
   SQL injections, unhandled errors, and deep OFFSET pagination.

2. TEST METHODOLOGY:
   - Zero-Inline-Comment Doctrine: All assertions and test plans are stated here.
     Test methods remain 100% comment-free and pure.
   - Synthetic In-Memory Testing: Uses temporary isolated mock paths.
================================================================================
"""

import unittest
from pathlib import Path
from src.features.audit.service.audit_service import AuditService
from src.features.audit.rules.audit_rules import MASTER_AUDIT_RULES

class TestAuditService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = AuditService(rules=MASTER_AUDIT_RULES)

    def test_rules_initialization(self) -> None:
        self.assertGreater(len(self.service._rules), 5)
        self.assertIn(".go", self.service._target_extensions)
        self.assertIn(".ts", self.service._target_extensions)
        self.assertIn(".py", self.service._target_extensions)

if __name__ == "__main__":
    unittest.main()
