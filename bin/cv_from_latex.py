#!/usr/bin/env python3
"""Generate _data/cv.yml from an Awesome-CV LaTeX project.

The LaTeX project (edited on Overleaf) is the single source of truth for CV
content. This script parses its macros and rewrites _data/cv.yml, so the
website's /cv/ page can never drift from the Overleaf document.

Usage:
    python3 bin/cv_from_latex.py <path-to-cv-repo> [-o _data/cv.yml]

Design notes:
  * The parser is deliberately STRICT. If it meets a macro shape it does not
    recognise, or a section file it cannot read, it raises. Stopping loudly is
    the point: silent mis-parsing would reintroduce exactly the drift this
    script exists to remove.
  * A few fields have no source in the LaTeX (the prose `summary`, `image`,
    and the structured `address`). Those are preserved from the existing
    _data/cv.yml on each run — edit them there, not here.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import OrderedDict

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")


# --------------------------------------------------------------------------
# LaTeX lexing helpers
# --------------------------------------------------------------------------


def strip_comments(tex: str) -> str:
    """Remove LaTeX line comments, honouring the \\% escape."""
    out = []
    for line in tex.splitlines():
        idx = None
        for i, ch in enumerate(line):
            if ch == "%" and (i == 0 or line[i - 1] != "\\"):
                idx = i
                break
        out.append(line if idx is None else line[:idx])
    return "\n".join(out)


def read_group(s: str, pos: int) -> tuple[str, int]:
    """Read one balanced {...} group starting at or after `pos`.

    Returns (contents, index just past the closing brace).
    """
    while pos < len(s) and s[pos] in " \t\r\n":
        pos += 1
    if pos >= len(s) or s[pos] != "{":
        raise ValueError(f"expected '{{' at offset {pos}: {s[pos : pos + 60]!r}")
    depth, start = 0, pos
    while pos < len(s):
        ch = s[pos]
        if ch == "\\":  # skip escaped char
            pos += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1 : pos], pos + 1
        pos += 1
    raise ValueError(f"unbalanced braces from offset {start}")


def find_macro(tex: str, name: str, nargs: int) -> list[list[str]]:
    """Return the argument lists of every `\\name{..}{..}` occurrence."""
    results = []
    pattern = re.compile(r"\\" + re.escape(name) + r"(?![a-zA-Z])")
    pos = 0
    while True:
        m = pattern.search(tex, pos)
        if not m:
            return results
        cursor = m.end()
        args = []
        try:
            for _ in range(nargs):
                arg, cursor = read_group(tex, cursor)
                args.append(arg)
        except ValueError as exc:
            raise ValueError(f"\\{name} near offset {m.start()}: {exc}") from exc
        results.append(args)
        pos = cursor


def _replace_macro(s: str, name: str, nargs: int, fmt) -> str:
    """Rewrite every `\\name{..}` into `fmt(args)`, innermost-safe."""
    pattern = re.compile(r"\\" + re.escape(name) + r"(?![a-zA-Z])")
    while True:
        m = pattern.search(s)
        if not m:
            return s
        cursor = m.end()
        args = []
        for _ in range(nargs):
            arg, cursor = read_group(s, cursor)
            args.append(arg)
        s = s[: m.start()] + fmt(args) + s[cursor:]


SIMPLE_SUBS = [
    (r"\\LaTeX(?![a-zA-Z])", "LaTeX"),
    (r"\\TeX(?![a-zA-Z])", "TeX"),
    (r"\\newline(?![a-zA-Z])", " "),
    (r"\\par(?![a-zA-Z])", " "),
    (r"\\quad(?![a-zA-Z])", " "),
    (r"\\,", " "),
    (r"\\&", "&"),
    (r"\\%", "%"),
    (r"\\\$", "$"),
    (r"\\#", "#"),
    (r"\\_", "_"),
    (r"~", " "),
    (r"``", '"'),
    (r"''", '"'),
    (r"---", "\u2014"),
    (r"--", "\u2013"),
]


def tex_to_text(s: str) -> str:
    """Convert an inline LaTeX fragment to Markdown-ish plain text."""
    if s is None:
        return ""
    s = strip_comments(s)

    # URLs are held aside while the text substitutions run: rules like
    # "~" -> " " are right for prose and catastrophic inside a URL
    # (https://ece.ut.ac.ir/en/~kargahi would silently lose its tilde).
    vault: dict[str, str] = {}

    def stow(url: str) -> str:
        key = f"\x00URL{len(vault)}\x00"
        vault[key] = url.strip()
        return key

    # Links first: they carry nested markup in their label.
    s = _replace_macro(s, "href", 2, lambda a: f"[{tex_to_text(a[1])}]({stow(a[0])})")
    s = _replace_macro(s, "url", 1, lambda a: stow(a[0]))

    # Math-mode superscripts mark equal contribution: $^{*}$ -> *
    s = re.sub(r"\$\^\{([^}]*)\}\$", r"\1", s)
    s = re.sub(r"\^\{([^}]*)\}", r"\1", s)

    for macro in ("textbf", "bfseries"):
        s = _replace_macro(s, macro, 1, lambda a: f"**{tex_to_text(a[0])}**")
    for macro in ("emph", "textit"):
        s = _replace_macro(s, macro, 1, lambda a: f"_{tex_to_text(a[0])}_")
    s = _replace_macro(s, "texttt", 1, lambda a: f"`{tex_to_text(a[0])}`")
    for macro in ("descriptionstyle", "textsc", "text", "mbox"):
        s = _replace_macro(s, macro, 1, lambda a: tex_to_text(a[0]))
    s = _replace_macro(s, "faIcon", 1, lambda a: "")
    s = _replace_macro(s, "slides", 1, lambda a: f"[Slides]({a[0].strip()})")

    # Environments and spacing macros that carry no text.
    s = re.sub(r"\\(begin|end)\{[^}]*\}(\{[^}]*\})?", " ", s)
    s = re.sub(r"\\vspace\*?\{[^}]*\}", " ", s)
    s = re.sub(r"\\hspace\*?\{[^}]*\}", " ", s)

    for pattern, repl in SIMPLE_SUBS:
        s = re.sub(pattern, repl, s)

    s = re.sub(r"[ \t\r\n]+", " ", s)
    s = s.strip()
    for key, url in vault.items():
        s = s.replace(key, url)
    return s


def tex_items(block: str) -> list[str]:
    """Split a cvitems block into a list of bullet strings."""
    if "\\item" not in block:
        text = tex_to_text(block)
        return [text] if text else []
    parts = re.split(r"\\item(?![a-zA-Z])", block)[1:]
    items = []
    for part in parts:
        part = part.strip()
        if part.startswith("{"):
            try:
                inner, _ = read_group(part, 0)
                part = inner
            except ValueError:
                pass
        text = tex_to_text(part)
        if text:
            items.append(text)
    return items


# --------------------------------------------------------------------------
# Date parsing
# --------------------------------------------------------------------------

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
# Each entry is (first month, last month) so that "Fall 2022 - Spring 2023"
# spans Sep 2022 - Jun 2023 rather than collapsing to single months.
SEASONS = {
    "spring": (2, 6),
    "summer": (7, 9),
    "fall": (9, 12),
    "autumn": (9, 12),
    "winter": (1, 3),
}
MONTH_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept|Sep|Oct|Nov|Dec|Spring|Summer|Fall|Autumn|Winter)\b\.?",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


def _month_span(token: str) -> tuple[int, int]:
    """Return (first month, last month) for a month or season token."""
    key = token.strip().rstrip(".").lower()
    if key in SEASONS:
        return SEASONS[key]
    number = MONTHS[key[:4] if key[:4] in MONTHS else key[:3]]
    return number, number


def parse_dates(raw: str) -> tuple[str | None, str | None]:
    """Turn an Awesome-CV date label into (start, end) as YYYY-MM / YYYY.

    Handles 'Sep. 2025 - Present', 'Jan.--Feb. 2025', 'Mar. 1--12, 2027',
    'Fall 2022 - Spring 2023 - Fall 2023', bare '2025', and empty strings.
    """
    text = tex_to_text(raw)
    if not text:
        return None, None

    is_present = bool(re.search(r"\b(present|current|ongoing)\b", text, re.IGNORECASE))
    years = [(m.start(), int(m.group())) for m in YEAR_RE.finditer(text)]
    if not years:
        return (None, "present") if is_present else (None, None)

    months = [(m.start(), _month_span(m.group())) for m in MONTH_RE.finditer(text)]

    points: list[tuple[int, tuple[int, int] | None]] = []
    if months:
        for mpos, span in months:
            year = next((y for ypos, y in years if ypos > mpos), years[-1][1])
            points.append((year, span))
    else:
        points = [(y, None) for _, y in years]

    def fmt(point: tuple[int, tuple[int, int] | None], which: int) -> str:
        year, span = point
        return f"{year}-{span[which]:02d}" if span else str(year)

    start = fmt(points[0], 0)
    end = "present" if is_present else fmt(points[-1], 1)
    return start, end


# --------------------------------------------------------------------------
# Section builders
# --------------------------------------------------------------------------


def _entry_dates(raw: str, target: dict) -> None:
    start, end = parse_dates(raw)
    if start:
        target["start_date"] = start
    if end:
        target["end_date"] = end


def build_education(tex: str) -> list[dict]:
    out = []
    for degree, institution, location, dates, body in find_macro(tex, "cventry", 5):
        entry = OrderedDict()
        entry["institution"] = tex_to_text(institution)
        if location.strip():
            entry["location"] = tex_to_text(location)
        entry["studyType"] = tex_to_text(degree)
        _entry_dates(dates, entry)
        highlights = tex_items(body)
        if highlights:
            entry["highlights"] = highlights
        out.append(entry)
    return out


SUPERVISOR_RE = re.compile(
    r"^\s*(?:under the supervision of|supervised by|co-supervised by)\s+", re.IGNORECASE
)


def build_experience(tex: str) -> list[dict]:
    out = []
    for position, company, location, dates, body in find_macro(tex, "cventry", 5):
        entry = OrderedDict()
        org = tex_to_text(company)
        role = tex_to_text(position)
        match = SUPERVISOR_RE.match(org)
        if match:
            # Organisation slot holds a supervisor line; the real affiliation
            # is in the location slot. Promote it and fold the supervisor
            # into the role, so the heading names the lab.
            entry["company"] = tex_to_text(location)
            supervisor = org[match.end():].strip()
            entry["position"] = f"{role} \u2014 {supervisor}" if supervisor else role
        else:
            entry["company"] = org
            entry["position"] = role
            if location.strip():
                entry["location"] = tex_to_text(location)
        _entry_dates(dates, entry)
        items = tex_items(body)
        if len(items) == 1:
            entry["summary"] = items[0]
        elif items:
            entry["highlights"] = items
        out.append(entry)
    return out


def build_awards(tex: str) -> list[dict]:
    out = []
    for title, awarder, location, date in find_macro(tex, "cvhonor", 4):
        entry = OrderedDict()
        entry["title"] = tex_to_text(title)
        start, end = parse_dates(date)
        if end:
            entry["date"] = end
        entry["awarder"] = tex_to_text(awarder)
        if location.strip():
            entry["location"] = tex_to_text(location)
        out.append(entry)
    return out


def build_tchentries(tex: str, kind: str) -> list[dict]:
    """\\tchentry is used for both teaching roles and certificates."""
    out = []
    for first, second, third, dates, _body in find_macro(tex, "tchentry", 5):
        entry = OrderedDict()
        if kind == "certificates":
            entry["name"] = tex_to_text(first)
            start, end = parse_dates(dates)
            if end:
                entry["date"] = end
            issuer = tex_to_text(second)
            provider = tex_to_text(third)
            if issuer and provider and provider.lower() not in issuer.lower():
                issuer = f"{issuer} ({provider})"
            entry["issuer"] = issuer
        else:
            entry["company"] = tex_to_text(second)
            entry["position"] = tex_to_text(first)
            if third.strip():
                entry["location"] = tex_to_text(third)
            _entry_dates(dates, entry)
        out.append(entry)
    return out


def build_projects(tex: str) -> list[dict]:
    out = []
    for title, name, category, dates, body in find_macro(tex, "cventry", 5):
        entry = OrderedDict()
        label = tex_to_text(name)
        descriptor = tex_to_text(title)
        entry["name"] = f"{label} \u2014 {descriptor}" if descriptor else label
        items = tex_items(body)
        if items:
            entry["summary"] = " ".join(items)
        start, end = parse_dates(dates)
        if start:
            entry["start_date"] = start
        if end:
            entry["end_date"] = end
        out.append(entry)
    return out


def build_skills(tex: str, key: str) -> list[dict]:
    out = []
    for category, detail in find_macro(tex, "cvskill", 2):
        entry = OrderedDict()
        entry["name"] = tex_to_text(category)
        entry[key] = tex_to_text(detail)
        out.append(entry)
    return out


def build_interests(tex: str) -> list[dict]:
    items = tex_items(tex)
    keywords = ", ".join(i.replace("**", "").strip() for i in items if i.strip())
    if not keywords:
        return []
    return [OrderedDict([("name", "Research"), ("keywords", keywords)])]


def _clean_author(chunk: str) -> str:
    """Drop equal-contribution markers without eating a Markdown bold close.

    "**MT. Fakharian***" -> "**MT. Fakharian**"   (marker removed, bold kept)
    "A. Ghalambor*"      -> "A. Ghalambor"
    """
    name = chunk.strip().rstrip(".").strip()
    if name.startswith("**"):
        match = re.match(r"^(\*\*.*?\*\*)[*\u2020\u2021]*$", name, re.S)
        return match.group(1) if match else name
    return name.rstrip("*\u2020\u2021").strip()


PUB_RE = re.compile(r"^(?P<authors>.*?)\((?P<year>\d{4})\)\.\s*(?P<rest>.*)$", re.S)


def build_publications(tex: str) -> list[dict]:
    """Parse the free-form `\\href{url}{\\descriptionstyle{...}}` publication lines."""
    out = []
    for url, body in find_macro(tex, "href", 2):
        text = tex_to_text(body)
        if not text:
            continue
        match = PUB_RE.match(text)
        if not match:
            raise ValueError(
                "publication line did not match 'Authors (Year). \"Title.\" Venue.':\n  " + text
            )
        rest = match.group("rest").strip()
        title_match = re.match(r'\**"(?P<title>.+?)\.?"\**\.?\s*(?P<venue>.*)$', rest, re.S)
        if not title_match:
            raise ValueError("could not find a quoted title in: " + rest)

        authors = []
        for chunk in re.split(r",(?![^(]*\))", match.group("authors")):
            authors_name = _clean_author(chunk)
            if authors_name:
                authors.append(authors_name)

        entry = OrderedDict()
        entry["title"] = title_match.group("title").strip()
        entry["authors"] = authors
        venue = title_match.group("venue").strip()
        if venue:
            entry["publisher"] = venue.replace("_", "").strip().rstrip(".")
        entry["releaseDate"] = match.group("year")
        entry["url"] = url.strip()
        out.append(entry)
    return out


# --------------------------------------------------------------------------
# Header (identity + socials)
# --------------------------------------------------------------------------

SOCIAL_MACROS = [
    ("github", "GitHub"),
    ("linkedin", "LinkedIn"),
    ("xaccount", "X"),
    ("twitter", "X"),
    ("gitlab", "GitLab"),
    ("orcid", "ORCID"),
    ("mastodon", "Mastodon"),
]


def build_header(tex: str) -> dict:
    header = OrderedDict()

    names = find_macro(tex, "name", 2)
    if not names:
        raise ValueError("cv.tex has no \\name{first}{last}")
    header["name"] = f"{tex_to_text(names[0][0])} {tex_to_text(names[0][1])}".strip()

    for macro, key in (("position", "label"), ("email", "email"), ("address", "location")):
        found = find_macro(tex, macro, 1)
        if found:
            value = tex_to_text(found[0][0])
            if value:
                header[key] = re.sub(r"\{|\}", "", value)

    socials = []
    for macro, network in SOCIAL_MACROS:
        found = find_macro(tex, macro, 1)
        if found and found[0][0].strip():
            socials.append(
                OrderedDict([("network", network), ("username", tex_to_text(found[0][0]))])
            )
    scholar = find_macro(tex, "googlescholar", 2)
    if scholar and scholar[0][0].strip():
        socials.append(
            OrderedDict(
                [("network", "Google Scholar"), ("username", tex_to_text(scholar[0][0]))]
            )
        )
    if socials:
        header["social_networks"] = socials
    return header


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

# Section label -> (source file, builder). Order here is the order on the page.
SECTIONS = [
    ("Education", "education.tex", build_education),
    ("Experience", ["researchExp.tex", "industrialExp.tex"], build_experience),
    ("Publications", "publications.tex", build_publications),
    ("Talks", "presentation.tex", build_experience),
    ("Awards", "honors.tex", build_awards),
    ("Service", "committees.tex", build_experience),
    ("Teaching", "teaching.tex", lambda t: build_tchentries(t, "teaching")),
    ("Projects", "academicProjects.tex", build_projects),
    ("Certificates", "licenses.tex", lambda t: build_tchentries(t, "certificates")),
    ("Skills", "skills.tex", lambda t: build_skills(t, "keywords")),
    ("Languages", "languages.tex", lambda t: build_skills(t, "summary")),
    ("Interests", "researchInterests.tex", build_interests),
]

# Fields with no LaTeX source; carried over from the existing _data/cv.yml.
PRESERVED_FIELDS = ("summary", "image", "address")


def read_tex(root: str, filename: str) -> str:
    path = os.path.join(root, "cv", filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"missing CV section file: {path}")
    with open(path, encoding="utf-8") as handle:
        return strip_comments(handle.read())


def build_cv(root: str, previous: dict | None) -> dict:
    main_path = os.path.join(root, "cv.tex")
    if not os.path.exists(main_path):
        raise FileNotFoundError(f"not an Awesome-CV project (no cv.tex): {root}")
    with open(main_path, encoding="utf-8") as handle:
        main = strip_comments(handle.read())

    # Only parse the section files cv.tex actually \input{}s.
    included = {
        os.path.basename(arg[0].strip())
        for arg in find_macro(main, "input", 1)
    }
    included |= {name if name.endswith(".tex") else name + ".tex" for name in list(included)}

    cv = build_header(main)

    prev_cv = (previous or {}).get("cv", {}) or {}
    for field in PRESERVED_FIELDS:
        if field in prev_cv:
            cv[field] = prev_cv[field]

    sections = OrderedDict()
    for label, sources, builder in SECTIONS:
        files = [sources] if isinstance(sources, str) else sources
        entries: list[dict] = []
        for filename in files:
            if filename not in included:
                print(f"  skip {label}: {filename} is not \\input by cv.tex", file=sys.stderr)
                continue
            entries.extend(builder(read_tex(root, filename)))
        if entries:
            sections[label] = entries
            print(f"  {label}: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")
        else:
            print(f"  {label}: (empty, omitted)")
    cv["sections"] = sections
    return {"cv": cv}


class _Dumper(yaml.SafeDumper):
    """Block style, stable key order, no PyYAML aliases."""

    def ignore_aliases(self, data):
        return True


def _represent_ordereddict(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


_Dumper.add_representer(OrderedDict, _represent_ordereddict)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="path to the Awesome-CV project (contains cv.tex)")
    parser.add_argument("-o", "--output", default="_data/cv.yml")
    args = parser.parse_args()

    previous = None
    if os.path.exists(args.output):
        with open(args.output, encoding="utf-8") as handle:
            previous = yaml.safe_load(handle)

    print(f"Parsing {args.source}")
    data = build_cv(args.source, previous)

    banner = (
        "# GENERATED FILE - DO NOT EDIT BY HAND.\n"
        "#\n"
        "# Rebuilt from the Awesome-CV LaTeX project on Overleaf by\n"
        "# bin/cv_from_latex.py -- run `bin/sync-cv` after editing on Overleaf.\n"
        "# Edit the CV on Overleaf; this file follows.\n"
        f"# Exceptions, preserved across regeneration: {', '.join(PRESERVED_FIELDS)}.\n"
    )
    body = yaml.dump(
        data,
        Dumper=_Dumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=100000,
    )
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(banner + body)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
