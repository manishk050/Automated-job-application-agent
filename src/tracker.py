"""Tracker for JobSweep demo.

Logs submitted applications to applied.json and held roles to
reviewed.json. Demo only, fake data only. This module never submits
an application, it only records what happened.
No em dashes in this file.
"""

import argparse
import json
import os
import sys
from datetime import date


def log_entry(job, status):
    """Build one tracker entry for a job. No file is written here."""
    return {
        "date": date.today().isoformat(),
        "company": job.get("company"),
        "title": job.get("title"),
        "posting_url": job.get("posting_url"),
        "posting_id": job.get("posting_id"),
        "status": status,
    }


def append_to_file(entry, path):
    """Append one entry to a JSON list file, creating it if needed."""
    records = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            records = json.load(f)
    records.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    return len(records)


def log_applied(job, path="applied.json"):
    """Log a submitted application. Returns the new total count."""
    return append_to_file(log_entry(job, "applied"), path)


def log_reviewed(job, path="reviewed.json"):
    """Log a role held for review. Returns the new total count."""
    return append_to_file(log_entry(job, "reviewed"), path)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Demo tracker entry for a job.")
    parser.add_argument("--job", default="examples/sample-job.json",
                        help="Path to a job JSON file.")
    parser.add_argument("--status", default="reviewed",
                        choices=["applied", "reviewed"],
                        help="Status to log. Default is reviewed.")
    parser.add_argument("--write", action="store_true",
                        help="Write to applied.json or reviewed.json. Without this flag, print only.")
    args = parser.parse_args(argv)

    with open(args.job, encoding="utf-8") as f:
        job = json.load(f)

    entry = log_entry(job, args.status)
    print("Demo tracker entry, nothing submitted:")
    print(json.dumps(entry, indent=2))
    if args.write:
        path = "applied.json" if args.status == "applied" else "reviewed.json"
        total = append_to_file(entry, path)
        print("Wrote to %s. Total records now: %d" % (path, total))
    else:
        print("Not written to file. Use --write to write this demo entry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
