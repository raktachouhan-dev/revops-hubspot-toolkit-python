# RevOps HubSpot Toolkit (Python)

A small Python package that scores sales accounts against an ideal-customer profile (ICP) and syncs the best ones to HubSpot through the CRM v3 API. It is a RevOps / GTM systems demo that runs on fictional sample data.

It is the Python companion to [pe-account-scoring-n8n](https://github.com/raktachouhan-dev/pe-account-scoring-n8n). Both use the same scoring rules and give the same results on the same data.

## What it does
- `toolkit/scorer.py`: scores each account out of 100 (fund size, strategy, geography, recent fundraise, debt maturity) and assigns tier A, B or C.
- `toolkit/hubspot.py`: HubSpot companies client. It searches by domain, then creates or updates (upsert), retries on rate limits (429) and server errors, and raises clear errors.
- `toolkit/cli.py`: scores a CSV and optionally syncs Tier A accounts.
- `tests/`: 7 pytest tests. The scoring test checks the published results for all 8 sample firms.

## Run it
```bash
pip install -r requirements.txt
python -m toolkit.cli sample-data/pe_firms_sample.csv            # score only
python -m toolkit.cli sample-data/pe_firms_sample.csv --sync     # dry run: shows what would be created
export HUBSPOT_TOKEN=...                                         # private-app token
python -m toolkit.cli sample-data/pe_firms_sample.csv --sync --live   # real writes
python -m pytest
```

## Results on the sample data
| Tier | Firm | Score |
|---|---|---|
| A | Northfield Capital Partners | 100 |
| A | Alder Credit Advisors | 89 |
| A | Summit Ridge Credit | 82 |
| B | Meridian Buyout Group | 69 |
| B | Harbor Lane Real Assets | 52 |
| B | Brightwater Growth | 47 |
| C | Quill Street Capital | 28 |
| C | Kestrel Ventures | 18 |

## Design notes
- **Dry run is the default.** Nothing is written to HubSpot unless you pass `--live`.
- **Text booleans are parsed explicitly.** CSV values arrive as text, and the string `"false"` must not count as true. A test covers this.
- **Retries respect `Retry-After`.** Rate-limited calls back off, then fail with a clear error.

## Limits (honest)
- The HubSpot client is tested with mocked HTTP responses only. It has not been run against a live HubSpot account.
- All scoring weights are assumptions. Tune them on your own closed-won data.
- The `icp_score` property must exist on the HubSpot company object before a live sync, or HubSpot will reject the write.
- Sample firms are fictional and use `.example` domains.

MIT licensed.
