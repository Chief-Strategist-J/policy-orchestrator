"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CLI FILE STRUCTURE SUBCOMMAND TESTS
================================================================================
"""

import unittest
from io import StringIO
from unittest.mock import patch
from src.api.cli.main import build_parser, main

class TestCliFileStructure(unittest.TestCase):
    def test_cli_scaffold_feature(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["scaffold-feature", "auth_module", "--base-dir", "/tmp/test_cli_f", "--json"])
        self.assertEqual(args.subcommand, "scaffold-feature")
        self.assertEqual(args.feature_name, "auth_module")

    def test_cli_scaffold_package(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["scaffold-package", "billing_pkg", "--base-dir", "/tmp/test_cli_p", "--json"])
        self.assertEqual(args.subcommand, "scaffold-package")
        self.assertEqual(args.package_name, "billing_pkg")

    def test_cli_impact_analysis(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["impact", "auth_module", "--direction", "DOWNSTREAM", "--max-depth", "4", "--json"])
        self.assertEqual(args.subcommand, "impact")
        self.assertEqual(args.target_id, "auth_module")
        self.assertEqual(args.direction, "DOWNSTREAM")

    def test_cli_feature_map(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["feature-map", "auth_module", "--json"])
        self.assertEqual(args.subcommand, "feature-map")
        self.assertEqual(args.feature_name, "auth_module")

    def test_cli_graph_scan(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["graph-scan", "/tmp/test_cli_f", "--json"])
        self.assertEqual(args.subcommand, "graph-scan")
        self.assertEqual(args.root_dir, "/tmp/test_cli_f")

if __name__ == "__main__":
    unittest.main()
