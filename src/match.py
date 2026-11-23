"""Match filter for JobSweep demo.

Floor rule: in scope only if the experience range includes 0, 1, or 2 years.
A range starting at 3 or more years goes to review, never auto-apply.
No em dashes in this file. Demo code only, fake data only.
"""

import argparse
import json
import re
import sys


def parse_experience_range(job):
    """Return (min_years, max_years) as ints, or (None, None) if unknown.

    Accepts min_years / max_years fields, or a string such as
    "0-2 years", "0 to 2 years", or "3-5 years".
    """
    if "min_years" in job or "max_years" in job:
        try:
            low = job.get("min_years")
            high = job.get("max_years")
            low = int(low) if low is not None else None
            high = int(high) if high is not None else None
            return low, high
        except (TypeError, ValueError):
            return None, None
    text = str(job.get("experience_range", "") or "")
    nums = re.findall(r"\d+", text)
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    if len(nums) == 1:
        return int(nums[0]), int(nums[0])
    return None, None


def is_in_scope(job):
    """True only if the range includes 0, 1, or 2 years.

    That means the range must start at 2 or below. A range starting
    at 3 or more is out of scope for auto-apply.
    """
    low, _high = parse_experience_range(job)
    if low is None:
        return False
    return low <= 2


def skills_overlap(job, resume_skills):
    """Return the sorted list of skills shared by the job and the resume."""
    wanted = [(str(s).strip(), str(s).strip().lower()) for s in job.get("skills", [])]
    have = {str(s).strip().lower() for s in resume_skills}
    return sorted([orig for orig, low in wanted if low in have])


def classify(job, resume_skills=None):
    """Classify a job as auto-apply, review, or out-of-scope.

    auto-apply: range includes 0, 1, or 2 years, and at least one
    skill overlaps with the resume.
    review: range starts at 3 or more, or no range is stated, or no
    skill overlaps. These wait for a human call, they are never
    auto-applied.
    """
    resume_skills = resume_skills or []
    low, _high = parse_experience_range(job)
    if low is None:
        return "review"
    if low >= 3:
        return "review"
    if resume_skills and not skills_overlap(job, resume_skills):
        return "review"
    return "auto-apply"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check if a job is in scope.")
    parser.add_argument("--check", required=True, help="Path to a job JSON file.")
    args = parser.parse_args(argv)

    with open(args.check, encoding="utf-8") as f:
        job = json.load(f)

    resume_skills = ["SQL", "Python", "Excel", "Power BI", "Tableau"]
    low, high = parse_experience_range(job)
    result = classify(job, resume_skills)
    overlap = skills_overlap(job, resume_skills)
    print("Job: %s at %s" % (job.get("title"), job.get("company")))
    print("Experience range: %s to %s years" % (low, high))
    print("In scope (0-2 years): %s" % is_in_scope(job))
    print("Skill overlap: %s" % (", ".join(overlap) if overlap else "none"))
    print("Classification: %s" % result)
    if result == "review":
        print("Action: send to review queue, do not auto-apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
