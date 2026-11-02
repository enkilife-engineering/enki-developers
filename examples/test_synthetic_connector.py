"""Bounded offline contract checks, not runtime isolation/security acceptance."""
import unittest
from synthetic_connector import CONNECTOR, CONTRACT, Denied, invoke


class ContractChecks(unittest.TestCase):
    def setUp(self):
        self.request = dict(contract=CONTRACT, request_id="demo-01", connector=CONNECTOR,
                            operation="catalog.list", resource="synthetic://catalog", limit=2)
        self.grant = dict(subject="synthetic-developer", tenant="synthetic-only", audience=CONNECTOR,
                          scopes=["catalog:read"], resource="synthetic://catalog", expires_at=101, revoked=False)

    def test_bounded_synthetic_success(self):
        result = invoke(self.request, self.grant, 100)
        self.assertTrue(result["synthetic"])
        self.assertEqual(len(result["records"]), 2)
        self.assertEqual(result["request_id"], "demo-01")
        self.request["limit"] = 1
        self.assertEqual(len(invoke(self.request, self.grant, 100)["records"]), 1)

    def test_write_and_arbitrary_resources_denied(self):
        for field, value in [("operation", "catalog.delete"), ("resource", "file:///private"),
                             ("resource", "https://example.invalid"), ("connector", "core"),
                             ("contract", "enki.connector/1")]:
            with self.subTest(field=field, value=value), self.assertRaises(Denied):
                invoke(dict(self.request, **{field: value}), self.grant, 100)

    def test_cross_tenant_subject_audience_scope_and_revocation_denied(self):
        for field, value in [("tenant", "other"), ("subject", "other"), ("audience", "core"),
                             ("scopes", []), ("scopes", ["catalog:read", "write"]), ("revoked", True)]:
            with self.subTest(field=field), self.assertRaises(Denied):
                invoke(self.request, dict(self.grant, **{field: value}), 100)

    def test_expiry_exact_boundary_denied(self):
        with self.assertRaises(Denied):
            invoke(self.request, self.grant, 101)

    def test_malformed_and_unknown_fields_denied(self):
        for request in [None, {}, dict(self.request, command="execute"),
                        dict(self.request, request_id="line\nbreak"), dict(self.request, limit=True),
                        dict(self.request, limit=3), dict(self.request, limit=0)]:
            with self.subTest(request=request), self.assertRaises(Denied):
                invoke(request, self.grant, 100)
        with self.assertRaises(Denied):
            invoke(self.request, dict(self.grant, token="not-a-token"), 100)


if __name__ == "__main__":
    unittest.main()
