"""Conservative, heading-based resume section suggestions.

No LLM is used. A suggestion is *not* verified profile data until the
authenticated user explicitly reviews and confirms it.
"""

import re

PROFILE_FIELDS = (
    "professional_summary",
    "skills",
    "experience",
    "education",
    "projects",
    "certifications",
)
MAX_FIELD_CHARS = 10_000

# Only explicit headings are recognized; do not infer experience or qualifications.
_SECTION_ALIASES = {
    "professional_summary": (
        "summary", "professional summary", "profile summary",
        "personal profile", "career objective", "objective", "about me",
    ),
    "skills": (
        "skills", "technical skills", "core skills", "core competencies",
        "technical competencies", "tools and technologies",
        "technologies", "skills and tools",
    ),
    "experience": (
        "experience", "work experience", "professional experience",
        "employment history", "work history", "internship experience",
    ),
    "education": (
        "education", "academic background", "education and training",
        "academic qualifications", "qualifications",
    ),
    "projects": (
        "projects", "personal projects", "selected projects",
        "academic projects", "relevant projects", "technical projects",
    ),
    "certifications": (
        "certifications", "certificates", "professional certifications",
        "certifications and licenses", "licenses and certifications",
    ),
}


def _normalize_header(value: str) -> str:
    value = re.sub(r"^\s*(?:#{1,6}\s*|\d+[.)]\s*)", "", value)
    return re.sub(r"[\s&/+-]+", " ", value.strip().casefold()).strip()


_LOOKUP = {
    _normalize_header(alias): key
    for key, aliases in _SECTION_ALIASES.items()
    for alias in aliases
}


def _heading(line: str) -> tuple[str | None, str]:
    """Recognize a full heading, or a heading with same-line colon content."""
    candidate = line.strip()
    if len(candidate) > 250 or not candidate:
        return None, ""
    head, sep, rest = candidate.partition(":")
    key = _LOOKUP.get(_normalize_header(head.rstrip(":")))
    if key and (sep or len(candidate) <= 70):
        return key, rest.strip() if sep else ""
    return None, ""


def suggest_profile_fields(extracted_text: str) -> dict:
    """Return tentative sections and unclassified text, without inventing facts."""
    collected: dict[str, list[str]] = {field: [] for field in PROFILE_FIELDS}
    unclassified: list[str] = []
    warnings: list[str] = []
    current: str | None = None

    for line in extracted_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        heading, inline = _heading(stripped)
        if heading is not None:
            current = heading
            if inline:
                collected[current].append(inline)
        elif current is None:
            unclassified.append(stripped)
        else:
            collected[current].append(stripped)

    fields = {}
    for key in PROFILE_FIELDS:
        section = "\n".join(collected[key]).strip()
        if len(section) > MAX_FIELD_CHARS:
            warnings.append(
                f"Section '{key}' exceeds {MAX_FIELD_CHARS} characters; "
                "it was left unclassified for manual review."
            )
            unclassified.append(f"[{key}]\n{section}")
            fields[key] = None
        else:
            fields[key] = section or None

    if not any(fields.values()):
        warnings.append(
            "No recognized resume sections were extracted. "
            "Review the unclassified text and enter fields manually."
        )
    if unclassified:
        warnings.append(
            "Some resume text was not assigned to a profile field; "
            "review the unclassified_text before saving."
        )

    return {
        "suggested_fields": fields,
        "unclassified_text": "\n".join(unclassified),
        "warnings": warnings,
    }
