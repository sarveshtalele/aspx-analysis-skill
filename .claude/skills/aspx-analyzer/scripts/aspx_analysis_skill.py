#!/usr/bin/env python3
"""
ASPX Analysis Skill — Entry Point
==================================
Analyzes ASP.NET Web Forms applications (.aspx pages, .ascx user controls,
.master pages). Supports GitHub URLs AND local repository paths (including '.').

Builds a persistent JSON index on first run. Subsequent queries re-use the
cached index so 1000+ page repos are analysed once and queried instantly.
The index build itself streams (read -> parse -> discard, one file at a
time) and parallelizes across processes by default, so 10,000+ page repos
build without exhausting memory or the terminal — see --workers/--max-bytes/
--max-pages below. For a single consolidated business-logic report on truly
huge repos, aspx_business_analyzer.py in this same folder is the other option.

Usage:
    python aspx_analysis_skill.py <target> [options]

<target>:
    https://github.com/org/repo    — clone from GitHub (reuses an existing local
                                     copy named {repo} in the current directory
                                     instead of re-cloning, if one is present)
    /path/to/local/repo            — analyze an existing project directly, no
                                     clone at all — any local path already on disk
    .                              — current working directory

Options:
    --view project      Complete architecture overview (default)
    --view pages        All pages listed page-by-page (grouped by folder)
    --view functional   Pages grouped by business function
    --view component    Master pages + user controls catalog
    --view navigation   Page-to-page navigation map
    --page <name>       Deep-dive on one specific page (e.g. --page Login)
    --area <name>       Deep-dive on one functional area (e.g. --area Admin)
    --rebuild           Force re-index (ignore existing cached index)
    --output <dir>      Output directory (default: ./{repo_name}/)
    --save-report       Write the report to a .md file as well as stdout
    --workers N         Parallel parser processes for the index build
                        (default: CPU count, capped 8; 1 = serial/debug)
    --max-bytes N       Skip code-behind files larger than N bytes (default 1500000)
    --max-pages N       Cap number of .aspx pages parsed (default 0 = no cap)
    --fresh-clone       For a GitHub URL target: always clone fresh, even if a
                        local copy named {repo} already exists in the current
                        directory (default: reuse it, skip the clone)

Examples:
    python aspx_analysis_skill.py https://github.com/org/WebFormsApp
    python aspx_analysis_skill.py C:/Projects/MyApp --view functional
    python aspx_analysis_skill.py . --view pages --save-report
    python aspx_analysis_skill.py . --page Login
    python aspx_analysis_skill.py . --page ProductList
    python aspx_analysis_skill.py . --area Administration
    python aspx_analysis_skill.py . --area Orders --save-report
    python aspx_analysis_skill.py . --view component
    python aspx_analysis_skill.py . --rebuild --view project
    python aspx_analysis_skill.py . --rebuild --workers 8   # 10,000+ page repo
"""

import sys
import os
import io
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

# Ensure the engine package is importable regardless of caller's cwd.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# UTF-8 stdout on Windows — prevents UnicodeEncodeError for non-ASCII content.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from engine.aspx_stream   import build_index_streaming
from engine.aspx_indexer  import save_index, load_index
from engine.aspx_reporter import (
    generate_project_overview,
    generate_pages_report,
    generate_page_detail,
    generate_functional_report,
    generate_area_report,
    generate_component_report,
    generate_navigation_report,
)

_HELP = __doc__

VALID_VIEWS = {'project', 'pages', 'functional', 'component', 'navigation'}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_github_url(s: str) -> bool:
    return s.startswith('https://github.com/') or s.startswith('http://github.com/')


def _repo_name_from_url(url: str) -> str:
    name = url.rstrip('/').removesuffix('.git').split('/')[-1]
    return re.sub(r'[^\w\-]', '_', name)


def _force_rmtree(path: str) -> None:
    """shutil.rmtree(ignore_errors=True) silently fails to delete a fresh git
    clone on Windows — git marks packed objects read-only, and Python's
    rmtree doesn't clear that bit before unlinking, so the whole temp clone
    (not just the .git folder) is orphaned on every single GitHub-URL run.
    Clear the read-only bit and retry instead of swallowing the error."""
    def _on_error(func, p, _exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass
    shutil.rmtree(path, onerror=_on_error)


def _clone(url: str, target: str) -> None:
    print(f"  Cloning {url} …")
    r = subprocess.run(
        ['git', 'clone', '--depth=1', url, target],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git clone failed:\n{r.stderr.strip()}")
    print("  [ok] Clone complete")


def _report_suffix(view: str, page: str, area: str) -> str:
    if page:
        return f'_page_{re.sub(r"[^\\w]", "_", page)}'
    if area:
        return f'_area_{re.sub(r"[^\\w]", "_", area)}'
    return f'_{view}'


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run(
    target: str,
    view: str       = 'project',
    page: str       = None,
    area: str       = None,
    rebuild: bool   = False,
    output_dir: str = None,
    save_report: bool = False,
    workers: int    = None,
    max_bytes: int  = 1_500_000,
    max_pages: int  = 0,
    fresh_clone: bool = False,
) -> None:
    print(f"\n{'='*62}")
    print(f"  ASPX Analysis Skill")
    print(f"  Target : {target}")
    view_label = f"page:{page}" if page else f"area:{area}" if area else view
    print(f"  View   : {view_label}")
    print(f"{'='*62}\n")

    tmp_dir   = None
    repo_path = None
    repo_name = None

    try:
        # ---- 1. Resolve target ------------------------------------------------
        if _is_github_url(target):
            repo_name = _repo_name_from_url(target)
            existing_local = os.path.join(os.getcwd(), repo_name)
            if not fresh_clone and os.path.isdir(existing_local) and os.listdir(existing_local):
                # Already have this repo on disk (e.g. cloned once into a
                # persistent workspace) — reuse it instead of a redundant
                # temp clone. Real value on large repos: re-cloning this
                # skill's own reference project is a 1.4 GB, multi-minute
                # operation avoided entirely by this check.
                repo_path = existing_local
                print(f'[1/4] Found existing local copy: {repo_path} (skipping clone — '
                      f'use --fresh-clone to force a fresh one)')
            else:
                tmp_dir   = tempfile.mkdtemp(prefix='aspx_skill_')
                repo_path = os.path.join(tmp_dir, repo_name)
                print('[1/4] Cloning repository …')
                _clone(target, repo_path)
        else:
            repo_path = str(Path(target).resolve())
            if not os.path.isdir(repo_path):
                sys.exit(f"Error: path not found — {repo_path}")
            repo_name = Path(repo_path).name or 'project'
            print(f'[1/4] Local repo: {repo_path}')

        # ---- 2. Output dir ----------------------------------------------------
        out_dir = output_dir if output_dir else os.path.join(os.getcwd(), repo_name)
        os.makedirs(out_dir, exist_ok=True)
        index_path = os.path.join(out_dir, f'{repo_name}_aspx_index.json')

        # ---- 3. Load or build index -------------------------------------------
        if os.path.exists(index_path) and not rebuild:
            print(f'[2/4] Loading cached index: {index_path}')
            index = load_index(index_path)
            s = index['stats']
            print(f"      Pages: {s['total_pages']} | Controls: {s['total_controls']} | "
                  f"Masters: {s['total_masters']}")
        else:
            resolved_workers = workers if workers is not None else min(8, os.cpu_count() or 2)
            if rebuild and os.path.exists(index_path):
                print(f'[2/4] Rebuilding index (--rebuild flag set, workers={resolved_workers}) …')
            else:
                print(f'[2/4] Discovering + parsing ASPX files (workers={resolved_workers}, '
                      f'streaming) …')

            index = build_index_streaming(
                repo_path, repo_name, workers=resolved_workers,
                max_bytes=max_bytes, max_pages=max_pages, with_methods=False,
            )

            if not index['pages'] and not index['user_controls'] and not index['master_pages']:
                print('\n[!] No ASPX files found. Is this an ASP.NET Web Forms project?')
                print('    Expected files: *.aspx, *.ascx, *.master')
                return

            print('[3/4] Saving index …')
            save_index(index, index_path)

        # ---- 4. Generate report -----------------------------------------------
        print(f'[4/4] Generating report: {view_label} …')

        if page:
            content = generate_page_detail(index, page)
        elif area:
            content = generate_area_report(index, area)
        elif view == 'pages':
            content = generate_pages_report(index)
        elif view == 'functional':
            content = generate_functional_report(index)
        elif view == 'component':
            content = generate_component_report(index)
        elif view == 'navigation':
            content = generate_navigation_report(index)
        else:
            content = generate_project_overview(index)

        # ---- Output -----------------------------------------------------------
        print()
        print(content)
        print()

        if save_report:
            suffix      = _report_suffix(view, page, area)
            report_path = os.path.join(out_dir, f'{repo_name}_aspx{suffix}.md')
            Path(report_path).write_text(content, encoding='utf-8')
            print(f'[ok] Report saved → {report_path}')

        print(f'\nIndex : {index_path}')
        print('Tip   : re-run with different --view / --page / --area to explore.')
        print('        Add --rebuild to re-parse after source changes.')

    finally:
        if tmp_dir:
            _force_rmtree(tmp_dir)


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def _parse_args(argv: list) -> dict:
    args   = argv[1:]
    result = {
        'target':      None,
        'view':        'project',
        'page':        None,
        'area':        None,
        'rebuild':     False,
        'output_dir':  None,
        'save_report': False,
        'workers':     None,
        'max_bytes':   1_500_000,
        'max_pages':   0,
        'fresh_clone': False,
    }

    i = 0
    while i < len(args):
        a = args[i]
        if a in ('--help', '-h'):
            print(_HELP)
            sys.exit(0)
        elif a == '--view' and i + 1 < len(args):
            result['view'] = args[i + 1]; i += 2
        elif a == '--page' and i + 1 < len(args):
            result['page'] = args[i + 1]; i += 2
        elif a == '--area' and i + 1 < len(args):
            result['area'] = args[i + 1]; i += 2
        elif a == '--output' and i + 1 < len(args):
            result['output_dir'] = args[i + 1]; i += 2
        elif a == '--workers' and i + 1 < len(args):
            result['workers'] = int(args[i + 1]); i += 2
        elif a == '--max-bytes' and i + 1 < len(args):
            result['max_bytes'] = int(args[i + 1]); i += 2
        elif a == '--max-pages' and i + 1 < len(args):
            result['max_pages'] = int(args[i + 1]); i += 2
        elif a == '--rebuild':
            result['rebuild'] = True; i += 1
        elif a == '--save-report':
            result['save_report'] = True; i += 1
        elif a == '--fresh-clone':
            result['fresh_clone'] = True; i += 1
        elif not a.startswith('--') and result['target'] is None:
            result['target'] = a; i += 1
        else:
            i += 1

    return result


def main() -> None:
    if len(sys.argv) < 2:
        print(_HELP)
        sys.exit(1)

    opts = _parse_args(sys.argv)

    target = opts['target']
    if not target:
        sys.exit('Error: No target provided. Use a GitHub URL, local path, or "."')

    # '.' → current working directory
    if target == '.':
        target = os.getcwd()

    view = opts['view']
    if view not in VALID_VIEWS:
        print(f"[!] Unknown view '{view}'. Valid: {', '.join(VALID_VIEWS)}. Defaulting to 'project'.")
        view = 'project'

    run(
        target      = target,
        view        = view,
        page        = opts['page'],
        area        = opts['area'],
        rebuild     = opts['rebuild'],
        output_dir  = opts['output_dir'],
        save_report = opts['save_report'],
        workers     = opts['workers'],
        max_bytes   = opts['max_bytes'],
        max_pages   = opts['max_pages'],
        fresh_clone = opts['fresh_clone'],
    )


if __name__ == '__main__':
    main()
