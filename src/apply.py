"""Apply stub for JobSweep demo.

Demo mode refuses to submit. Even with --confirm, this file is only a
stub: it prints what it would do and returns without touching any portal,
without sending any request, and without using any password, OTP, or
captcha logic. A blocked portal is a stop, not a detour.
No em dashes in this file. Demo code only, fake data only.
"""

import argparse
import json
import sys


def submit(job, confirm=False):
    """Stub submit. Always returns False, nothing is ever submitted.

    Without --confirm, it refuses. With --confirm, it still only prints
    the planned action and returns False, because this demo repo has
    no real submit path.
    """
    title = job.get("title")
    company = job.get("company")
    url = job.get("posting_url")
    if not confirm:
        print("Refused: demo mode. %s at %s was NOT submitted." % (title, company))
        print("Run with --confirm to see the stub plan, still nothing is submitted.")
        return False
    print("STUB ONLY, nothing submitted:")
    print("Would submit %s at %s" % (title, company))
    print("Posting URL: %s" % url)
    print("This demo has no portal call, no login, and no form submit.")
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description="Demo apply stub. Submits nothing.")
    parser.add_argument("job", nargs="?", default="examples/sample-job.json",
                        help="Path to a job JSON file.")
    parser.add_argument("--confirm", action="store_true",
                        help="Show the stub plan. Still submits nothing.")
    args = parser.parse_args(argv)

    with open(args.job, encoding="utf-8") as f:
        job = json.load(f)

    submitted = submit(job, confirm=args.confirm)
    print("Submitted: %s" % submitted)
    return 0


if __name__ == "__main__":
    sys.exit(main())
