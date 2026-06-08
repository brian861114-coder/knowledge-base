#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from kb_paths import is_ignored_note_path, repo_root, resolve_vault_path
from validate_knowledge_base import parse_frontmatter


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
HEADING_RE = re.compile(r"^#{2,3}\s+(.+)$", re.MULTILINE)
VAGUE_PATTERNS = (
    "重要",
    "常見",
    "廣泛",
    "核心",
    "基本",
    "關鍵",
    "常用",
)

DEFAULT_LANGS = ("zh", "en")
USER_AGENT = "knowledge_map_wikipedia_enrichment/0.1"


def clean_text(value: str) -> str:
    value = re.sub(WIKILINK_RE, lambda match: match.group(2) or match.group(1), value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"\*([^*]+)\*", r"\1", value)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"^\s*[-*]\s+", "", value, flags=re.MULTILINE)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def extract_sections(body: str) -> list[dict]:
    matches = list(HEADING_RE.finditer(body))
    sections: list[dict] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = clean_text(body[start:end])
        sections.append(
            {
                "title": match.group(1).strip(),
                "content_preview": content[:320],
            }
        )
    return sections


def extract_wikilinks(body: str) -> list[str]:
    return [match.group(1).strip() for match in WIKILINK_RE.finditer(body)]


def load_note(path: Path, vault: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    return {
        "id": path.stem.strip().replace(" ", "-"),
        "path": path.relative_to(vault).as_posix(),
        "title": str(frontmatter.get("title", path.stem)).strip(),
        "type": str(frontmatter.get("type", "")).strip(),
        "domain": str(frontmatter.get("domain", "")).strip(),
        "taxonomy_domain": str(frontmatter.get("taxonomy_domain", "")).strip(),
        "summary": str(frontmatter.get("summary", "")).strip(),
        "frontmatter": frontmatter,
        "body": body,
        "clean_body": clean_text(body),
        "sections": extract_sections(body),
        "wikilinks": extract_wikilinks(body),
    }


def build_vault_index(vault: Path) -> dict:
    title_to_path: dict[str, str] = {}
    normalized_titles: dict[str, str] = {}
    for file_path in sorted(vault.rglob("*.md")):
        if is_ignored_note_path(file_path, vault):
            continue
        text = file_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(text)
        title = str(frontmatter.get("title", file_path.stem)).strip()
        rel_path = file_path.relative_to(vault).as_posix()
        title_to_path[title] = rel_path
        normalized_titles[normalize_target(title)] = title
        normalized_titles[normalize_target(file_path.stem)] = title
    return {
        "title_to_path": title_to_path,
        "normalized_titles": normalized_titles,
    }


def normalize_target(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def wiki_api_get(lang: str, params: dict) -> dict:
    encoded = urllib.parse.urlencode(params)
    url = f"https://{lang}.wikipedia.org/w/api.php?{encoded}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def search_wikipedia(query: str, lang: str, limit: int = 5) -> list[dict]:
    payload = wiki_api_get(
        lang,
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": str(limit),
            "utf8": "1",
            "format": "json",
        },
    )
    return payload.get("query", {}).get("search", [])


def fetch_page_evidence(title: str, lang: str) -> dict:
    lead_payload = wiki_api_get(
        lang,
        {
            "action": "query",
            "prop": "extracts|info|revisions",
            "titles": title,
            "redirects": "1",
            "exintro": "1",
            "explaintext": "1",
            "inprop": "url",
            "rvprop": "ids",
            "format": "json",
        },
    )
    parse_payload = wiki_api_get(
        lang,
        {
            "action": "parse",
            "page": title,
            "prop": "sections|links",
            "format": "json",
        },
    )

    page = next(iter(lead_payload.get("query", {}).get("pages", {}).values()), {})
    sections = parse_payload.get("parse", {}).get("sections", [])
    links = parse_payload.get("parse", {}).get("links", [])
    revisions = page.get("revisions", [])
    revision_id = revisions[0].get("revid") if revisions else None

    internal_links = [
        link.get("*", "").strip()
        for link in links
        if link.get("ns") == 0 and link.get("*")
    ]

    return {
        "title": page.get("title", title),
        "lang": lang,
        "pageid": page.get("pageid"),
        "canonical_url": page.get("canonicalurl"),
        "full_url": page.get("fullurl"),
        "revision_id": revision_id,
        "lead_extract": clean_text(page.get("extract", "")),
        "sections": [section.get("line", "").strip() for section in sections if section.get("line")],
        "internal_links": internal_links,
    }


def choose_match(note: dict, requested_lang: str | None, explicit_title: str | None) -> dict:
    languages = []
    if requested_lang:
        languages.append(requested_lang)
    for lang in DEFAULT_LANGS:
        if lang not in languages:
            languages.append(lang)

    if explicit_title:
        lang = requested_lang or note["frontmatter"].get("wikipedia_lang") or DEFAULT_LANGS[0]
        evidence = fetch_page_evidence(explicit_title, str(lang))
        return {
            "status": "explicit",
            "confidence": "high",
            "selected_page": evidence,
            "alternatives": [],
        }

    title = str(note["frontmatter"].get("wikipedia_title", "")).strip() or note["title"]
    alternatives: list[dict] = []
    for lang in languages:
        results = search_wikipedia(title, lang)
        if not results:
            continue
        for result in results:
            alternatives.append(
                {
                    "title": result.get("title", ""),
                    "lang": lang,
                    "snippet": clean_text(result.get("snippet", "")),
                    "wordcount": result.get("wordcount"),
                }
            )
        best = results[0]
        evidence = fetch_page_evidence(best.get("title", title), lang)
        confidence = "medium"
        if normalize_target(best.get("title", "")) == normalize_target(title):
            confidence = "high"
        return {
            "status": "matched",
            "confidence": confidence,
            "selected_page": evidence,
            "alternatives": alternatives[:5],
        }

    return {
        "status": "manual_match_required",
        "confidence": "low",
        "selected_page": None,
        "alternatives": alternatives[:5],
    }


def analyze_note(note: dict) -> dict:
    weaknesses: list[str] = []
    strengths: list[str] = []

    summary = note["summary"]
    if not summary:
        weaknesses.append("missing_summary")
    elif len(summary) < 40:
        weaknesses.append("summary_too_short")
    elif any(pattern in summary for pattern in VAGUE_PATTERNS):
        weaknesses.append("summary_looks_vague")
    else:
        strengths.append("summary_has_some_specificity")

    if not note["sections"]:
        weaknesses.append("no_structured_sections")
    elif len(note["sections"]) >= 4:
        strengths.append("has_multiple_sections")

    if len(note["wikilinks"]) < 3:
        weaknesses.append("few_internal_links")
    else:
        strengths.append("has_internal_links")

    relation_counts = {
        field: len(value) if isinstance(value, list) else (1 if value else 0)
        for field, value in note["frontmatter"].items()
        if field in {"prerequisites", "related_concepts", "related_quantities", "related_laws", "experiments", "math_tools"}
    }
    if sum(relation_counts.values()) == 0:
        weaknesses.append("few_frontmatter_relations")
    else:
        strengths.append("has_frontmatter_relations")

    opening_preview = note["clean_body"][:260]
    if any(pattern in opening_preview for pattern in VAGUE_PATTERNS):
        weaknesses.append("opening_paragraph_looks_vague")

    return {
        "weaknesses": weaknesses,
        "strengths": strengths,
        "current_sections": [section["title"] for section in note["sections"]],
        "current_links": note["wikilinks"],
        "current_relations": relation_counts,
    }


def build_revision_plan(note: dict, evidence: dict | None, vault_index: dict) -> dict:
    if not evidence:
        return {
            "definition_gaps": ["manual_wikipedia_match_required"],
            "missing_key_terms": [],
            "missing_section_topics": [],
            "recommended_related_notes": [],
            "recommended_prerequisites": [],
            "phrases_to_replace": [],
            "keep_sections": [section["title"] for section in note["sections"]],
            "rewrite_sections": [],
        }

    existing_titles = vault_index["normalized_titles"]
    related_matches: list[str] = []
    for link in evidence["internal_links"]:
        normalized = normalize_target(link)
        if normalized in existing_titles:
            related_matches.append(existing_titles[normalized])
    related_matches = sorted(dict.fromkeys(related_matches))

    current_sections = {section["title"] for section in note["sections"]}
    missing_sections = [section for section in evidence["sections"] if section and section not in current_sections][:8]

    phrases_to_replace: list[str] = []
    for pattern in VAGUE_PATTERNS:
        if pattern in note["summary"] or pattern in note["clean_body"][:200]:
            phrases_to_replace.append(pattern)

    return {
        "definition_gaps": [
            "replace_vague_opening_with_concrete_definition",
            "anchor_definition_to_functional_role_or mathematical identity" if note["type"] == "mathematical_tool" else "anchor_definition_to_physical meaning",
        ],
        "missing_key_terms": evidence["internal_links"][:12],
        "missing_section_topics": missing_sections,
        "recommended_related_notes": related_matches[:12],
        "recommended_prerequisites": related_matches[:5],
        "phrases_to_replace": sorted(dict.fromkeys(phrases_to_replace)),
        "keep_sections": [section["title"] for section in note["sections"]],
        "rewrite_sections": [note["sections"][0]["title"]] if note["sections"] else [],
    }


def build_prompt_packet(note: dict, match: dict, analysis: dict, revision_plan: dict) -> dict:
    return {
        "task": "rewrite_note_from_wikipedia_evidence",
        "note_title": note["title"],
        "note_type": note["type"],
        "domain": note["domain"],
        "taxonomy_domain": note["taxonomy_domain"],
        "rewrite_constraints": [
            "do not directly copy long Wikipedia passages",
            "preserve the existing note type and taxonomy",
            "do not add wikilinks that do not already resolve in the vault context list",
            "rewrite vague definitions into concrete instructional wording",
            "prefer internal consistency with the existing knowledge base over encyclopedic filler",
        ],
        "analysis": analysis,
        "revision_plan": revision_plan,
        "matched_wikipedia_page": match.get("selected_page"),
        "vault_context_allowed_related_notes": revision_plan.get("recommended_related_notes", []),
        "original_note": {
            "summary": note["summary"],
            "body": note["clean_body"],
            "sections": note["sections"],
        },
    }


def resolve_note_path(vault: Path, note_path: str | None, note_title: str | None) -> Path:
    if note_path:
        path = Path(note_path)
        if not path.is_absolute():
            path = vault / path
        return path.resolve()
    if not note_title:
        raise SystemExit("Provide either --note-path or --note-title.")
    for file_path in vault.rglob("*.md"):
        if is_ignored_note_path(file_path, vault):
            continue
        text = file_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(text)
        title = str(frontmatter.get("title", file_path.stem)).strip()
        if title == note_title or file_path.stem == note_title:
            return file_path.resolve()
    raise SystemExit(f"Note not found for title: {note_title}")


def ensure_output_path(note_id: str, out_path: str | None) -> Path:
    if out_path:
        return Path(out_path).resolve()
    root = repo_root() / "tmp" / "wikipedia_enrichment"
    root.mkdir(parents=True, exist_ok=True)
    return (root / f"{note_id}.json").resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Wikipedia-backed enrichment report for a knowledge-base note.")
    parser.add_argument("--vault", help="Vault path. Falls back to .knowledge-base.local.json")
    parser.add_argument("--note-path", help="Path to the note inside the vault")
    parser.add_argument("--note-title", help="Note title if you do not want to pass a path")
    parser.add_argument("--wiki-title", help="Explicit Wikipedia page title override")
    parser.add_argument("--lang", help="Preferred Wikipedia language, e.g. zh or en")
    parser.add_argument("--out", help="Output JSON file path")
    args = parser.parse_args()

    vault = resolve_vault_path(args.vault)
    note_path = resolve_note_path(vault, args.note_path, args.note_title)
    note = load_note(note_path, vault)
    vault_index = build_vault_index(vault)
    match = choose_match(note, args.lang, args.wiki_title)
    analysis = analyze_note(note)
    revision_plan = build_revision_plan(note, match.get("selected_page"), vault_index)
    prompt_packet = build_prompt_packet(note, match, analysis, revision_plan)

    payload = {
        "note": {
            "id": note["id"],
            "path": note["path"],
            "title": note["title"],
            "type": note["type"],
            "domain": note["domain"],
            "taxonomy_domain": note["taxonomy_domain"],
            "summary": note["summary"],
            "sections": note["sections"],
            "wikilinks": note["wikilinks"],
        },
        "match": match,
        "wikipedia_evidence": match.get("selected_page"),
        "analysis": analysis,
        "revision_plan": revision_plan,
        "prompt_packet": prompt_packet,
    }

    out_path = ensure_output_path(note["id"], args.out)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote enrichment report to {out_path}")


if __name__ == "__main__":
    main()
