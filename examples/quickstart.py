"""Run from the pack root: python3 -B -m examples.quickstart"""
from sdk import SyntheticClient


def main():
    fixture_grant = dict(subject="synthetic-developer", tenant="synthetic-only",
                         audience="synthetic.catalog", scopes=["catalog:read"],
                         resource="synthetic://catalog", expires_at=101, revoked=False)
    page = SyntheticClient().list_catalog(request_id="quickstart-01", grant=fixture_grant, now=100)
    for record in page.records:
        print(record.id, record.title, record.source)


if __name__ == "__main__":
    main()
