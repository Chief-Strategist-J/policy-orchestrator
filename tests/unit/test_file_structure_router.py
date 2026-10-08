"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FILE STRUCTURE REST ROUTER INTEGRATION TESTS
================================================================================
"""

import unittest
from fastapi.testclient import TestClient
from src.api.rest.app import app

class TestFileStructureRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_scaffold_feature_endpoint(self) -> None:
        payload = {
            "featureName": "billing_v2",
            "baseDir": "/tmp/test_routes_src",
            "withRouter": True,
            "withHandler": True,
            "portType": "local",
        }
        res = self.client.post("/api/v1/file-structure/scaffold/feature", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["feature"], "billing_v2")

    def test_get_feature_map_endpoint(self) -> None:
        res = self.client.get("/api/v1/file-structure/feature/billing_v2")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["feature"], "billing_v2")
        self.assertIn("context", data["data"])
        self.assertIn("types", data["data"])
        self.assertIn("schema", data["data"])
        self.assertIn("router", data["data"])
        self.assertIn("handler", data["data"])
        self.assertIn("service", data["data"])

    def test_impact_analysis_endpoint(self) -> None:
        payload = {
            "targetId": "billing_v2",
            "direction": "UPSTREAM",
            "maxDepth": 4,
        }
        res = self.client.post("/api/v1/file-structure/impact-analysis", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["target_id"], "billing_v2")

    def test_scaffold_package_endpoint(self) -> None:
        payload = {
            "packageName": "test_pkg_delivery",
            "baseDir": "/tmp/test_pkg_dest",
        }
        res = self.client.post("/api/v1/file-structure/scaffold/package", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["package"], "test_pkg_delivery")

    def test_link_files_endpoint(self) -> None:
        payload = {
            "source": "src/features/billing/service/billing_service.py",
            "relType": "IMPORTS_SHARED",
            "target": "src/shared/utils/formatters.py",
        }
        res = self.client.post("/api/v1/file-structure/link-files", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["data"]["linked"])

    def test_create_file_endpoint(self) -> None:
        payload = {
            "filePath": "/tmp/test_custom_rules.py",
            "role": "RuleSet",
            "relType": "ENFORCES_RULES",
            "targetFileOrNode": "billing_v2",
            "direction": "incoming",
        }
        res = self.client.post("/api/v1/file-structure/create-file", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["role"], "RuleSet")

if __name__ == "__main__":
    unittest.main()

