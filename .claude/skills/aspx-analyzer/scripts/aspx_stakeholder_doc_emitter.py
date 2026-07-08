#!/usr/bin/env python3
"""
ASPX Stakeholder Documentation Emitter
========================================
Reads the JSON index (aspx_analysis_skill.py / aspx_business_analyzer.py) and,
if present, an OpenSpec workspace's in-flight changes, and emits ONE
business-facing markdown document for non-technical stakeholders:

  - Executive summary of the legacy application (real data, not boilerplate)
  - Business capability inventory with risk flags
  - Current modernization status (real per-change progress, if openspec/
    already has changes; otherwise a "not started yet" note)
  - Where to start — the single lowest-risk capability, named concretely
  - How to build the complete project end-to-end (the SDD loop, generically)
  - Governance/quality controls summary

Reuses the same capability scoring as aspx_roadmap_emitter.py (imported, not
duplicated) so "where to start" always matches the roadmap's own ranking.

No third-party dependencies; does not require the `openspec` CLI to be
installed — reads openspec/changes/*/tasks.md directly as plain text.

Usage:
    python aspx_stakeholder_doc_emitter.py <index.json> [--openspec-dir DIR] [--output DIR]
"""

import sys
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from aspx_roadmap_emitter import _score_capability, _pick_starting_page

_HELP = __doc__

_CHECKBOX_DONE   = re.compile(r'^\s*-\s*\[[xX]\]', re.MULTILINE)
_CHECKBOX_TOTAL  = re.compile(r'^\s*-\s*\[[ xX]\]', re.MULTILINE)


# ---------------------------------------------------------------------------
# OpenSpec progress scanning — plain file reads, no `openspec` CLI dependency
# ---------------------------------------------------------------------------

def _scan_openspec_progress(openspec_dir: str) -> List[Dict[str, Any]]:
    """Read openspec/changes/*/tasks.md directly; return per-change progress.
    Does not invoke the openspec CLI — safe to run even if it isn't installed."""
    changes_dir = os.path.join(openspec_dir, 'changes')
    specs_dir = os.path.join(openspec_dir, 'specs')
    if not os.path.isdir(changes_dir):
        return []

    results = []
    for name in sorted(os.listdir(changes_dir)):
        change_path = os.path.join(changes_dir, name)
        if name == 'archive' or not os.path.isdir(change_path):
            continue
        tasks_path = os.path.join(change_path, 'tasks.md')
        done = total = 0
        if os.path.isfile(tasks_path):
            text = Path(tasks_path).read_text(encoding='utf-8', errors='replace')
            done = len(_CHECKBOX_DONE.findall(text))
            total = len(_CHECKBOX_TOTAL.findall(text))
        has_proposal = os.path.isfile(os.path.join(change_path, 'proposal.md'))
        # Archived == its spec folder exists under openspec/specs/ with the
        # same slug (best-effort match; exact capability->spec-folder naming
        # depends on the proposal's own Capabilities section).
        archived = os.path.isdir(os.path.join(specs_dir, name)) if os.path.isdir(specs_dir) else False
        results.append({
            'name': name,
            'has_proposal': has_proposal,
            'tasks_done': done,
            'tasks_total': total,
            'archived': archived,
        })
    return results


# ---------------------------------------------------------------------------
# Content builders
# ---------------------------------------------------------------------------

def _executive_summary(index: dict) -> str:
    s = index.get('stats', {})
    wc = index.get('web_config', {})
    project = index.get('project', 'this application')
    areas = index.get('functional_areas', {})

    lines = [
        f"**{project}** is an ASP.NET Web Forms application comprising "
        f"**{s.get('total_pages', 0)} pages**, **{s.get('total_controls', 0)} reusable "
        f"components**, and **{s.get('total_masters', 0)} shared layout templates**, "
        f"organized into **{s.get('total_functional_areas', len(areas))} business "
        f"capabilities**.",
        "",
    ]
    if wc.get('auth_mode'):
        lines.append(f"- **Access control**: {wc['auth_mode']} authentication.")
    if s.get('pages_with_sql_direct'):
        lines.append(
            f"- **Data-access risk**: {s['pages_with_sql_direct']} page(s) access a "
            f"database directly from page code — the primary technical risk driver "
            f"for migration planning."
        )
    unknown_auth = s.get('auth_breakdown', {}).get('unknown', 0)
    if unknown_auth:
        lines.append(
            f"- **Access-control gap**: {unknown_auth} page(s) have no automatically "
            f"detectable authorization requirement — each should be manually confirmed "
            f"before its capability is migrated, not assumed."
        )
    return '\n'.join(lines)


def _capability_table(index: dict) -> str:
    page_index = {p['rel_path']: p for p in index.get('pages', [])}
    areas = index.get('functional_areas', {})
    ranked = []
    for area, pages in areas.items():
        stats = _score_capability(pages, page_index)
        ranked.append((area, stats))
    ranked.sort(key=lambda r: r[1]['score'])

    lines = [
        "| Capability | Pages | Data-Access Risk | Relative Complexity |",
        "|---|---|---|---|",
    ]
    for area, s in ranked:
        risk = "High" if s['sql'] > 0 else ("Medium" if s['ajax'] > 0 else "Low")
        complexity = "Low" if s['score'] < 10 else ("Medium" if s['score'] < 50 else "High")
        lines.append(f"| {area} | {s['pages']} | {risk} | {complexity} |")
    return '\n'.join(lines)


def _status_section(progress: List[Dict[str, Any]]) -> str:
    if not progress:
        return (
            "No modernization work has started yet — no OpenSpec changes exist. "
            "See **Getting Started** below for the recommended first capability."
        )
    lines = [
        "| Capability (Change) | Progress | Status |",
        "|---|---|---|",
    ]
    for p in progress:
        if p['tasks_total']:
            progress_str = f"{p['tasks_done']}/{p['tasks_total']} tasks"
        elif p['has_proposal']:
            progress_str = "planning in progress"
        else:
            progress_str = "not started"
        status = "Complete (archived)" if p['archived'] else (
            "In progress" if p['tasks_done'] else "Planned"
        )
        lines.append(f"| {p['name']} | {progress_str} | {status} |")
    return '\n'.join(lines)


def _getting_started(index: dict) -> str:
    page_index = {p['rel_path']: p for p in index.get('pages', [])}
    areas = index.get('functional_areas', {})
    if not areas:
        return "No business capabilities were identified in the analysis."

    ranked = []
    for area, pages in areas.items():
        stats = _score_capability(pages, page_index)
        start_page = _pick_starting_page(pages, page_index) if pages else None
        ranked.append((area, stats, start_page, pages))
    ranked.sort(key=lambda r: r[1]['score'])

    top_area, top_stats, top_page, top_pages = ranked[0]
    first_page_label = (
        f"`{top_page['rel_path'].replace(chr(92), '/')}`" if top_page else "its first page"
    )

    return (
        f"The recommended first capability is **{top_area}** ({top_stats['pages']} page(s), "
        f"lowest complexity score in the analysis, {top_stats['sql']} direct database "
        f"dependencies). Start with {first_page_label} — it is the single lowest-risk unit "
        f"of work identified, making it the right choice to prove the delivery process "
        f"before committing to higher-complexity capabilities."
    )


_HOW_TO_BUILD = """\
Every capability — starting with the one above, then every subsequent one — follows the
same four-stage planning process before any implementation begins:

1. **Proposal** — why this capability needs to change, what changes, what is
   explicitly out of scope.
2. **Design** — the technical approach and key decisions.
3. **Specification** — the exact required behavior, stated as testable scenarios.
4. **Task Plan** — the ordered, checkable implementation steps.

Implementation only begins once all four are authored and reviewed, and only follows the
Task Plan exactly. A task is marked complete only once its outcome has been genuinely
observed — not merely coded. A capability is only finalized once every task is verified
this way.

**To build the complete project**: repeat this process for every capability in the table
above, working from lowest to highest complexity. Completion means every capability has
been through this cycle and its behavior is recorded as durable specification —
`openspec/specs/` fully populated is the definition of "done," not a percentage estimate.
"""

_GOVERNANCE = """\
| Control | What it ensures |
|---|---|
| Review gate before implementation | No code is written until the plan has been reviewed |
| Verification discipline | A task is complete only when observed working, never assumed |
| Legacy traceability | Every proposal names the exact legacy page(s) it replaces |
| Access-control continuity | Existing authorization requirements are preserved unless a change is explicitly proposed |
"""


def build_document(index: dict, progress: List[Dict[str, Any]]) -> str:
    project = index.get('project', 'Project')
    lines = [
        f"# {project} — Stakeholder Overview & Modernization Guide",
        "",
        "*Generated from automated analysis of the application source code.*",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        _executive_summary(index),
        "",
        "---",
        "",
        "## Business Capability Inventory",
        "",
        _capability_table(index),
        "",
        "---",
        "",
        "## Current Modernization Status",
        "",
        _status_section(progress),
        "",
        "---",
        "",
        "## Getting Started",
        "",
        _getting_started(index),
        "",
        "---",
        "",
        "## How to Build the Complete Project, End to End",
        "",
        _HOW_TO_BUILD,
        "---",
        "",
        "## Quality & Governance Controls",
        "",
        _GOVERNANCE,
    ]
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(_HELP)
        sys.exit(0 if args else 1)

    index_path = args[0]
    openspec_dir: Optional[str] = None
    output_dir: Optional[str] = None

    i = 1
    while i < len(args):
        if args[i] == '--openspec-dir' and i + 1 < len(args):
            openspec_dir = args[i + 1]; i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output_dir = args[i + 1]; i += 2
        else:
            i += 1

    if not os.path.isfile(index_path):
        sys.exit(f"Error: index file not found — {index_path}")

    with open(index_path, 'r', encoding='utf-8') as f:
        index = json.load(f)

    progress = _scan_openspec_progress(openspec_dir) if openspec_dir else []
    content = build_document(index, progress)

    out_dir = output_dir or os.path.dirname(os.path.abspath(index_path))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'STAKEHOLDER_DOCUMENTATION.md')
    Path(out_path).write_text(content, encoding='utf-8')

    print(f"[ok] Stakeholder documentation saved -> {out_path}")
    if openspec_dir and not progress:
        print(f"  (no changes found under {openspec_dir}/changes — reported as 'not started')")


if __name__ == '__main__':
    main()
