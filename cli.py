"""Score a CSV of accounts and optionally sync them to HubSpot.

python -m toolkit.cli sample-data/pe_firms_sample.csv            # score only
python -m toolkit.cli sample-data/pe_firms_sample.csv --sync     # dry-run sync (no writes)
python -m toolkit.cli sample-data/pe_firms_sample.csv --sync --live   # real writes
"""
import argparse
import csv

from .hubspot import HubSpotClient
from .scorer import score_account


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("csv_path")
    p.add_argument("--sync", action="store_true", help="sync Tier A accounts to HubSpot")
    p.add_argument("--live", action="store_true", help="really write to HubSpot (default is dry run)")
    args = p.parse_args(argv)

    with open(args.csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    scored = sorted(((r, score_account(r)) for r in rows), key=lambda x: -x[1].score)
    for r, s in scored:
        print(f"{s.tier}  {s.score:>3}  {r['name']:<30} {s.breakdown}")

    if args.sync:
        client = HubSpotClient(dry_run=not args.live)
        for r, s in scored:
            if s.tier == "A":
                action, cid = client.upsert_company(r["domain"], {"name": r["name"], "icp_score": s.score})
                print(f"HubSpot: {action} {r['name']} ({cid})")


if __name__ == "__main__":
    main()
