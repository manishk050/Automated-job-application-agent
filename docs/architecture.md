# JobSweep architecture

Demo version. Real system results, for reference only: 130 applications in 6 weeks, about 475 boards scanned, 0-2 year filter, live at jobsweep.tech at Rs 99. The demo below uses fake sample data only and submits nothing.

## Pipeline

```
Hourly sweep -> Freshness check -> Match filter -> Dedupe -> Tailor -> Review queue / Apply -> Tracker
```

## Stages

### 1. Hourly sweep

`src/sweep.py` scans a board list on an hourly schedule. In this demo repo, `--demo` scans only 3 fake jobs and makes no network call. In the real system, the sweep covers Lever and Greenhouse boards plus other company career pages.

### 2. Freshness check

Only roles posted in the last 30 days count. Freshness comes from the source timestamp, such as Lever `createdAt` or Greenhouse `first_published`, not from a search engine date label. In the demo, freshness comes from the `posted_date` or `days_ago` field. A role posted 40 days ago is skipped as stale, even if it matches on skills.

### 3. Match filter

`src/match.py` applies the floor rule: in scope only if the experience range includes 0, 1, or 2 years. A range starting at 3 or more years goes to review, never auto-apply. A role with no stated range also goes to review. Skills must truthfully overlap with the resume, otherwise the role goes to review too.

### 4. Dedupe

`src/dedupe.py` checks every lead against applied and reviewed records by posting URL and posting ID first, never by company name alone. The posting ID is extracted from the URL with a regex, UUID first, then a run of 6 or more digits. The same posting under two different URLs is still one posting, and one company can have many different postings.

### 5. Tailor

`src/tailor.py` builds a 1-page tailored note outline from a master template placeholder. It highlights only skills that are both asked for and on the resume. A missing skill is flagged as a gap for a human call, it is never added to the resume by this code.

### 6. Review queue / Apply

Clear junior matches go to apply. Senior, borderline, or stale roles go to the review queue and wait for a human call. `src/apply.py` in this demo is a stub only: it refuses in demo mode, and even with `--confirm` it only prints what it would do and returns without touching any portal.

Referral-first rule: for each new auto-apply role, one quick search for a publicly listed recruiter or hiring-manager email. If one is found, one referral request goes out and the application is held. If there is no reply in 24 hours, a decline, or no public email, apply as is. Never guess an email.

### 7. Tracker

`src/tracker.py` logs submitted applications to `applied.json` and held roles to `reviewed.json`, with date, company, title, posting URL, and posting ID. In the demo, the sweep only prints what it would log. The tracker CLI prints an entry by default and only writes a file with `--write`.

## Files

- `src/sweep.py`: demo scan, freshness, orchestration
- `src/match.py`: floor rule and skill overlap
- `src/dedupe.py`: posting ID extraction and duplicate check
- `src/tailor.py`: tailored outline, gap flagging
- `src/apply.py`: stub only, submits nothing
- `src/tracker.py`: applied and reviewed logging
- `config/boards.example.yaml`: board list shape, fake boards only
- `examples/sample-job.json`: one fake posting
- `examples/sample-tailored-note.md`: tailoring outline for the sample job

## Safety rules

- Demo mode never submits an application and never touches a real portal.
- No passwords, OTP handling, or captcha workarounds in this repo. A blocked portal is a stop, not a detour.
- No real companies, no real resume, no real applied records in this repo.
