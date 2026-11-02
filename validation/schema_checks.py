"""Optional authoring check: jsonschema==4.23.0; never required by the SDK."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jsonschema import Draft202012Validator
from examples.synthetic_connector import demonstration


class SchemaChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {name: json.loads((ROOT / "contracts" / (name + ".schema.json")).read_text())
                       for name in ("request", "response", "fixture-grant")}
        cls.validators = {k: Draft202012Validator(v) for k, v in cls.schemas.items()}

    def request(self):
        return dict(contract="enki.connector/0.1-draft", request_id="schema-01",
                    connector="synthetic.catalog", operation="catalog.list",
                    resource="synthetic://catalog", limit=2)

    def grant(self):
        return dict(subject="synthetic-developer", tenant="synthetic-only", audience="synthetic.catalog",
                    scopes=["catalog:read"], resource="synthetic://catalog", expires_at=101, revoked=False)

    def test_all_schemas_validate_against_metaschema(self):
        for name, value in self.schemas.items():
            with self.subTest(schema=name):
                Draft202012Validator.check_schema(value)

    def test_positive_contract_documents(self):
        for name, value in [("request", self.request()), ("fixture-grant", self.grant()),
                            ("response", demonstration())]:
            with self.subTest(schema=name):
                self.validators[name].validate(value)

    def test_request_rejections(self):
        for field, value in [("request_id", "schema-01\n"), ("limit", True), ("limit", 0),
                             ("limit", 3), ("operation", "catalog.delete"), ("resource", "file:///private"),
                             ("contract", "next"), ("command", "run")]:
            with self.subTest(field=field, value=value):
                self.assertFalse(self.validators["request"].is_valid(dict(self.request(), **{field: value})))

    def test_grant_rejections(self):
        for field, value in [("tenant", "other"), ("subject", "other"), ("audience", "core"),
                             ("scopes", ["write"]), ("revoked", True), ("expires_at", True),
                             ("token", "unwanted")]:
            with self.subTest(field=field):
                self.assertFalse(self.validators["fixture-grant"].is_valid(dict(self.grant(), **{field: value})))

    def test_response_rejections(self):
        for field, value in [("synthetic", False), ("next_cursor", "cursor"), ("records", []),
                             ("records", demonstration()["records"] * 2), ("command", "run")]:
            with self.subTest(field=field):
                self.assertFalse(self.validators["response"].is_valid(dict(demonstration(), **{field: value})))

    def test_record_rejections(self):
        for field, value in [("source", "https://example.invalid"), ("title", "x" * 129),
                             ("text", "x" * 1025), ("text", "ending-newline\n"),
                             ("text", "ending-delete\x7f"), ("text", 1)]:
            value_copy = copy.deepcopy(demonstration())
            value_copy["records"][0][field] = value
            with self.subTest(field=field):
                self.assertFalse(self.validators["response"].is_valid(value_copy))

    def test_relational_constraints_remain_sdk_responsibility(self):
        # Schema alone cannot establish request correlation or current authority.
        from sdk import ContractError, validate_response
        response = demonstration()
        response["request_id"] = "different-request"
        self.assertTrue(self.validators["response"].is_valid(response))
        with self.assertRaises(ContractError):
            validate_response(response, "demo-01", 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
