from docx import Document
from typing import List
import re


def parse_docx(path: str):
    """Parse a .docx file and return a simple JSON structure.

    Returns: {"title": str, "paragraphs": [str, ...]}
    """
    try:
        doc = Document(path)
    except Exception:
        return {"title": "Resume", "paragraphs": [f"Unable to read resume file: {path}"]}

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    title = paragraphs[0] if paragraphs else "Resume"
    return {"title": title, "paragraphs": paragraphs}


def merge_docx(paths: List[str]):
    """Parse multiple .docx files and merge their content.

    Strategy: keep order, skip empty paragraphs and remove exact duplicates while preserving first occurrence.
    Returns the same structure as `parse_docx` with combined paragraphs.
    """
    combined = []
    title = None
    seen = set()
    for p in paths:
        if not p:
            continue
        data = parse_docx(p)
        if not title and data.get("title"):
            title = data["title"]
        for para in data.get("paragraphs", []):
            if para in seen:
                continue
            seen.add(para)
            combined.append(para)

    if not title:
        title = "Resume"
    return {"title": title, "paragraphs": combined}


def build_profile(paths: List[str]):
    """Merge docx files and extract simple structured profile data.

    Returned keys: title, name, summary, linkedin, github, projects (list), paragraphs (other)
    """
    merged = merge_docx(paths)
    paras = merged.get("paragraphs", [])

    name = paras[0] if paras else merged.get("title", "Resume")
    summary = ""
    linkedin = ""
    github = ""
    projects = []
    other = []

    url_re = re.compile(r"(https?://\S+)")

    for p in paras[1:]:
        low = p.lower()
        if not linkedin and "linkedin" in low:
            m = url_re.search(p)
            linkedin = m.group(1) if m else p.strip()
            continue
        if not github and "github" in low:
            m = url_re.search(p)
            github = m.group(1) if m else p.strip()
            continue

        # project-like lines
        if re.search(r"\bproject\b", p, re.I) or p.strip().startswith("-") or "•" in p or re.match(r"^\d+\.", p.strip()):
            projects.append(p.strip())
            continue

        if not summary:
            summary = p.strip()
        else:
            other.append(p.strip())

    return {
        "title": merged.get("title", "Resume"),
        "name": name,
        "summary": summary,
        "linkedin": linkedin,
        "github": github,
        "projects": projects,
        "paragraphs": other,
    }

