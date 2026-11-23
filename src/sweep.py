"""Hourly sweep for JobSweep demo.

Demo only. `python src/sweep.py --demo` scans only fake sample jobs,
prints matches, and submits NOTHING. It touches no real portal, makes
no network call, and uses no real board list.
Freshness: only roles posted in the last 30 days count.
No em dashes in this file. Demo code only, fake data only.
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from match import classify, is_in_scope, parse_experience_range, skills_overlap
from dedupe import is_duplicate
from tracker import log_entry

FRESHNESS_DAYS = 30
RESUME_SKILLS = ["SQL", "Python", "Excel", "Power BI", "Tableau"]

SAMPLE_JOBS = [
    {
        "title": "Data Analyst",
        "company": "Example Analytics Pvt Ltd",
        "location": "Bangalore, India",
        "posting_url": "https://example-boards.test/jobs/demo-987654",
        "posting_id": "demo-987654",
        "min_years": 0,
        "max_years": 2,
        "skills": ["SQL", "Python", "Excel", "Power BI"],
        "days_ago": 2,
    },
    {
        "title": "Senior Data Analyst",
        "company": "Example Retail Co",
        "location": "Bangalore, India",
        "posting_url": "https://example-boards.test/jobs/demo-987655",
        "posting_id": "demo-987655",
        "min_years": 3,
        "max_years": 5,
        "skills": ["SQL", "Python", "Power BI"],
        "days_ago": 1,
    },
    {
        "title": "Data Analyst",
        "company": "Example Logistics Co",
        "location": "Remote, India",
        "posting_url": "https://example-boards.test/jobs/demo-987656",
        "posting_id": "demo-987656",
        "min_years": 0,
        "max_years": 2,
        "skills": ["SQL", "Excel"],
        "days_ago": 40,
    },
]


def posted_date_for(job):
    """Posted date for a demo job, from days_ago or a posted_date field."""
    if "days_ago" in job:
        return date.today() - timedelta(days=int(job["days_ago"]))
    text = str(job.get("posted_date", "") or "")
    try:
        year, month, day = [int(p) for p in text.split("-")]
        return date(year, month, day)
    except (ValueError, TypeError):
        return date.today()


def is_fresh(job, days=FRESHNESS_DAYS):
    """True only if the job was posted in the last 30 days."""
    posted = posted_date_for(job)
    age = (date.today() - posted).days
    return 0 <= age <= days


def scan_demo_jobs():
    """Scan the fake sample jobs. Returns a list of result dicts."""
    seen = []
    results = []
    for job in SAMPLE_JOBS:
        posted = posted_date_for(job)
        age = (date.today() - posted).days
        low, high = parse_experience_range(job)
        fresh = is_fresh(job)
        if not fresh:
            outcome = "skip, stale"
        else:
            outcome = classify(job, RESUME_SKILLS)
            if outcome == "auto-apply" and is_duplicate(job, seen):
                outcome = "skip, duplicate"
        results.append({
            "job": job,
            "age_days": age,
            "fresh": fresh,
            "in_scope": is_in_scope(job),
            "experience": "%s to %s years" % (low, high),
            "skill_overlap": skills_overlap(job, RESUME_SKILLS),
            "outcome": outcome,
        })
        seen.append(job)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="JobSweep demo sweep. Submits nothing.")
    parser.add_argument("--demo", action="store_true",
                        help="Run the demo scan on fake sample jobs only.")
    args = parser.parse_args(argv)

    if not args.demo:
        print("Demo only in this repo. Run with --demo.")
        print("No real boards are scanned and no application is submitted.")
        return 2

    print("JobSweep demo sweep, fake sample data only, nothing submitted.")
    print("Freshness window: last %d days. Boards scanned: 3 fake demo boards." % FRESHNESS_DAYS)
    print("")

    results = scan_demo_jobs()
    matches = 0
    for r in results:
        job = r["job"]
        day_word = "day" if r["age_days"] == 1 else "days"
        print("%s at %s, %s, posted %d %s ago" % (
            job["title"], job["company"], r["experience"], r["age_days"], day_word))
        print("  Fresh: %s, in scope (0-2 years): %s" % (r["fresh"], r["in_scope"]))
        print("  Skill overlap: %s" % ", ".join(r["skill_overlap"]))
        print("  Outcome: %s" % r["outcome"])
        if r["outcome"] == "auto-apply":
            matches += 1
            entry = log_entry(job, "would-apply-demo")
            print("  Tracker would log: %s" % entry)
        elif r["outcome"] == "review":
            entry = log_entry(job, "reviewed")
            print("  Tracker would log for review: %s" % entry)
        print("")

    print("Demo summary: %d match(es) for auto-apply, %d job(s) scanned." % (matches, len(results)))
    print("Submitted: 0 applications. This demo never submits anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
