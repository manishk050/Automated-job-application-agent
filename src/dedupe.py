"""Dedupe for JobSweep demo.

Dedupe by posting URL and posting ID first, never by company name alone.
The same posting can appear under different URLs, and one company can
have many different postings, so a company name check would fail both ways.
No em dashes in this file. Demo code only, fake data only.
"""

import argparse
import json
import os
import re
import sys

UUID_RE = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)
NUMERIC_RE = re.compile(r"(\d{6,})(?:[-/?]|$)")


def extract_posting_id(url):
    """Extract a posting ID from a URL, or None if there is none.

    Tries a UUID first, then a run of 6 or more digits, then a
    demo style id such as demo-987654. Returns the id lowercased.
    """
    if not url:
        return None
    text = str(url)
    m = UUID_RE.search(text)
    if m:
        return m.group(1).lower()
    m = NUMERIC_RE.search(text)
    if m:
        return m.group(1)
    m = re.search(r"demo-([A-Za-z0-9-]+)", text, re.IGNORECASE)
    if m:
        return "demo-" + m.group(1).lower()
    return None


def normalize_url(url):
    """Lowercase a URL and strip a trailing slash and query string."""
    if not url:
        return ""
    text = str(url).strip().lower()
    text = text.split("?", 1)[0].split("#", 1)[0]
    return text.rstrip("/")


def posting_id_of(job):
    """Return the posting id for a job dict, from its id or its URL."""
    if job.get("posting_id"):
        return str(job["posting_id"]).lower()
    return extract_posting_id(job.get("posting_url", ""))


def is_duplicate(job, seen):
    """True if this job is already in seen, by id first, then by URL.

    seen is a list of job dicts with posting_url and/or posting_id.
    Company name is never used here, by design.
    """
    job_id = posting_id_of(job)
    job_url = normalize_url(job.get("posting_url", ""))
    for old in seen:
        old_id = posting_id_of(old)
        if job_id and old_id and job_id == old_id:
            return True
        old_url = normalize_url(old.get("posting_url", ""))
        if job_url and old_url and job_url == old_url:
            return True
    return False


def load_seen(paths):
    """Load seen jobs from JSON files, skipping files that do not exist."""
    seen = []
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            seen.extend(data)
    return seen


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check if a job is a duplicate.")
    parser.add_argument("--check", required=True, help="Path to a job JSON file.")
    parser.add_argument("--seen", nargs="*", default=["applied.json", "reviewed.json"],
                        help="Seen files to check against. Defaults to applied.json and reviewed.json.")
    args = parser.parse_args(argv)

    with open(args.check, encoding="utf-8") as f:
        job = json.load(f)

    seen = load_seen(args.seen)
    print("Job: %s at %s" % (job.get("title"), job.get("company")))
    print("Posting URL: %s" % job.get("posting_url"))
    print("Posting ID: %s" % posting_id_of(job))
    print("Seen records checked: %d" % len(seen))
    if is_duplicate(job, seen):
        print("Result: DUPLICATE, already applied or reviewed, do not apply again.")
    else:
        print("Result: NEW, no matching posting ID or URL in seen records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
