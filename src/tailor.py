"""Resume tailoring outline for JobSweep demo.

Builds a 1-page tailored note outline from a master template placeholder.
Tailoring means highlighting real matches, never inventing skills.
If the job asks for a skill that is not on the resume, it is listed as
a gap for a human call, it is never added to the resume here.
No em dashes in this file. Demo code only, fake data only.
"""

import argparse
import json
import sys

RESUME_SKILLS = ["SQL", "Python", "Excel", "Power BI", "Tableau", "PostgreSQL"]


def highlight_skills(job, resume_skills=None):
    """Skills the job asks for that are also on the resume."""
    resume_skills = resume_skills or RESUME_SKILLS
    wanted = [str(s).strip() for s in job.get("skills", [])]
    have_lower = {str(s).strip().lower() for s in resume_skills}
    return [s for s in wanted if s.lower() in have_lower]


def find_gaps(job, resume_skills=None):
    """Skills the job asks for that are NOT on the resume. Flag, do not add."""
    resume_skills = resume_skills or RESUME_SKILLS
    wanted = [str(s).strip() for s in job.get("skills", [])]
    have_lower = {str(s).strip().lower() for s in resume_skills}
    return [s for s in wanted if s.lower() not in have_lower]


def build_tailored_note(job, resume_skills=None):
    """Return a tailored outline dict. No resume text is invented here."""
    resume_skills = resume_skills or RESUME_SKILLS
    return {
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "posting_url": job.get("posting_url"),
        "headline": "Data Analyst | SQL, Python, Power BI, Excel",
        "skills_to_highlight": highlight_skills(job, resume_skills),
        "skills_gap_flag_for_human": find_gaps(job, resume_skills),
        "cover_letter_points": [
            "1-2 years of data analysis experience, in scope for this role.",
            "Matching skills from the list above, with real project examples.",
            "Immediate joiner, based in Bengaluru, India.",
        ],
        "note": "Master resume text is a placeholder in this demo repo. "
                "In the real system, a 1-page copy is built from the master "
                "resume, with matching skills reordered and emphasised.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a tailored note outline.")
    parser.add_argument("job", nargs="?", default="examples/sample-job.json",
                        help="Path to a job JSON file.")
    args = parser.parse_args(argv)

    with open(args.job, encoding="utf-8") as f:
        job = json.load(f)

    note = build_tailored_note(job)
    print("Tailored note outline for: %s at %s" % (note["title"], note["company"]))
    print("Headline: %s" % note["headline"])
    print("Skills to highlight: %s" % ", ".join(note["skills_to_highlight"]))
    gaps = note["skills_gap_flag_for_human"]
    print("Skills gap, flag for human, do not add: %s" % (", ".join(gaps) if gaps else "none"))
    print("Cover letter points:")
    for point in note["cover_letter_points"]:
        print("  - %s" % point)
    print(note["note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
