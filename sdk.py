"""Offline synthetic reference SDK. No production authentication or transport."""
from dataclasses import dataclass
from examples.synthetic_connector import CONTRACT, CONNECTOR, Denied, invoke


class ContractError(ValueError):
    """Untrusted response failed the draft contract."""


@dataclass(frozen=True)
class Record:
    id: str
    title: str
    text: str
    source: str


@dataclass(frozen=True)
class Page:
    request_id: str
    records: tuple[Record, ...]
    synthetic: bool = True
    next_cursor: None = None


def validate_response(value, request_id, limit):
    """Accept bounded synthetic data only. Never follow a source URI or render HTML."""
    if type(limit) is not int or not 1 <= limit <= 2:
        raise ContractError("invalid_limit")
    if (type(request_id) is not str or not 1 <= len(request_id) <= 64
            or not request_id.isascii() or not all(c.isalnum() or c in "-_" for c in request_id)):
        raise ContractError("invalid_request_id")
    if type(value) is not dict or set(value) != {"contract", "request_id", "synthetic", "records", "next_cursor"}:
        raise ContractError("invalid_response")
    if (value["contract"] != CONTRACT or value["request_id"] != request_id
            or value["synthetic"] is not True or value["next_cursor"] is not None):
        raise ContractError("response_binding")
    rows = value["records"]
    if type(rows) is not list or not 1 <= len(rows) <= limit:
        raise ContractError("record_limit")
    result, seen = [], set()
    for row in rows:
        if type(row) is not dict or set(row) != {"id", "title", "text", "source"}:
            raise ContractError("invalid_record")
        if any(type(row[k]) is not str for k in row):
            raise ContractError("invalid_record_type")
        if row["id"] not in {"demo-001", "demo-002"} or row["id"] in seen:
            raise ContractError("record_identity")
        if row["source"] != "synthetic://catalog/" + row["id"]:
            raise ContractError("untrusted_provenance")
        if not 1 <= len(row["title"]) <= 128 or not 1 <= len(row["text"]) <= 1024:
            raise ContractError("record_size")
        if any(ord(c) < 32 or ord(c) == 127 for c in row["title"] + row["text"]):
            raise ContractError("control_characters")
        seen.add(row["id"])
        result.append(Record(**row))
    return Page(request_id, tuple(result))


class SyntheticClient:
    """Only calls the fixed local fixture. Grants and time are explicit test data."""
    def list_catalog(self, *, request_id, grant, now, limit=2):
        request = dict(contract=CONTRACT, request_id=request_id, connector=CONNECTOR,
                       operation="catalog.list", resource="synthetic://catalog", limit=limit)
        return validate_response(invoke(request, grant, now), request_id, limit)
