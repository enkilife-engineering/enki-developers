"""Draft contract 0.1; synthetic in-memory data only; no ENKI integration.

The grant argument is a local test fixture, never an authentication mechanism.
No network, file reads, environment variables, credentials or core imports.
"""

CONTRACT = "enki.connector/0.1-draft"
CONNECTOR = "synthetic.catalog"
RECORDS = (
    ("demo-001", "Synthetic document index", "Example content; no real person or case."),
    ("demo-002", "Synthetic project note", "A fictional read-only integration demonstration."),
)


class Denied(ValueError):
    pass


def invoke(request, grant, now):
    """Validate a broker-verified grant fixture and return a bounded data response."""
    required = {"contract", "request_id", "connector", "operation", "resource", "limit"}
    if type(request) is not dict or set(request) != required:
        raise Denied("invalid_request")
    if request["contract"] != CONTRACT or request["connector"] != CONNECTOR:
        raise Denied("unsupported_contract_or_connector")
    rid = request["request_id"]
    if type(rid) is not str or not 1 <= len(rid) <= 64 or not rid.isascii() or not all(c.isalnum() or c in "-_" for c in rid):
        raise Denied("invalid_request_id")
    if request["operation"] != "catalog.list" or request["resource"] != "synthetic://catalog":
        raise Denied("unsupported_operation_or_resource")
    if type(request["limit"]) is not int or not 1 <= request["limit"] <= 2:
        raise Denied("invalid_limit")
    # Literal grants are deliberately valid only for this fictional tenant/subject.
    if type(grant) is not dict or set(grant) != {"subject", "tenant", "audience", "scopes", "resource", "expires_at", "revoked"}:
        raise Denied("invalid_grant")
    if (grant["subject"] != "synthetic-developer" or grant["tenant"] != "synthetic-only"
            or grant["audience"] != CONNECTOR or grant["scopes"] != ["catalog:read"]
            or grant["resource"] != request["resource"] or grant["revoked"] is not False):
        raise Denied("unauthorized")
    if type(now) is not int or type(grant["expires_at"]) is not int or now >= grant["expires_at"]:
        raise Denied("expired")
    return {"contract": CONTRACT, "request_id": rid, "synthetic": True,
            "records": [{"id": i, "title": t, "text": s, "source": "synthetic://catalog/" + i}
                        for i, t, s in RECORDS[:request["limit"]]], "next_cursor": None}


def demonstration():
    request = dict(contract=CONTRACT, request_id="demo-01", connector=CONNECTOR,
                   operation="catalog.list", resource="synthetic://catalog", limit=2)
    grant = dict(subject="synthetic-developer", tenant="synthetic-only", audience=CONNECTOR,
                 scopes=["catalog:read"], resource="synthetic://catalog", expires_at=101, revoked=False)
    return invoke(request, grant, now=100)


if __name__ == "__main__":
    import json
    print(json.dumps(demonstration(), indent=2))
