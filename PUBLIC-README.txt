ENKI Developer Network — offline synthetic developer preview (unreleased draft)

Explore a proposed read-only connector contract with two fictional records.
This source preview has no ENKI core access, production connector, network calls,
credentials, customer content or telemetry. The fixture grant is not authentication.
No production integration or independent security certification is offered.

Python 3.9+; standard library only for the SDK and quickstart. From this directory:
  python3 -B -m examples.quickstart
  python3 -B -m unittest test_sdk -v
  python3 -B -m unittest discover -s examples -p 'test_*.py' -v

Expected output: demo-001 and demo-002 with synthetic titles and source URIs.
Read sdk.py for SyntheticClient.list_catalog and immutable Page/Record results.
Invalid request/grant: Denied. Invalid response: ContractError. Neither exposes
raw input in its error. Text is untrusted data; source URIs are never followed.
The reference client only calls the fixed local example, with explicit fixture
grant and time. No external transport, plugin loader or automatic retries exist.

Contract enki.connector/0.1-draft, connector synthetic.catalog, catalog.list,
catalog:read, synthetic://catalog, limit 1–2. Unknown fields/versions/resources/
operations are refused. Responses bind to request ID and limit, source to record
ID, forbid duplicate IDs and enforce bounded strings. No writes or pagination.

contracts/*.schema.json document JSON Schema 2020-12 shapes. Runtime Python also
checks relationships that schemas cannot express, such as current expiry,
request/response correlation and source/ID matching. Schema integer semantics
can accept mathematically integral JSON numbers; Python fixture limits/timestamps
deliberately require actual int values and reject bool/float. No raw wire parser
is provided. A future transport must bound bytes before parsing and reject
duplicate keys, nonfinite numbers and excessive nesting.

Optional schema authoring checks use jsonschema==4.23.0 in a separate environment:
  python -B validation/schema_checks.py
The schema validator is not a runtime dependency. Versions and test limits are
recorded in the private review pack; no production compatibility/SLA is promised.

Contribution, conduct, security, privacy and licensing decisions are in policies/.
Maintainer: enkilife-engineering, subject to existing access and Founder controls.
Founder selected Apache-2.0 for the approved export (see LICENSE and licensing
scope). Final third-party/export review, confidential intake activation, independent
acceptance and publication approval remain separate. Other policies are draft.
Never post customer data, credentials or private ENKI source in contributions.
Draft 0.1 is the only supported synthetic protocol; breaking versions require
explicit new fixtures/review. No real connector version is currently supported.
