"""
ASPX File Loader
================
Discovers ASP.NET Web Forms files (.aspx, .ascx, .master, code-behind .cs,
web.config) from a repository directory.

Two-pass strategy for memory efficiency with 1000+ file repos:
  Pass 1 — Walk directory tree collecting only file PATHS (no content read).
            Build code-behind map: aspx_path -> cs_path.
  Pass 2 — Process one file at a time: read → parse → discard raw content.
            At most 2 file contents in memory at once (page + code-behind).
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

SKIP_DIRS = {
    '.git', 'bin', 'obj', 'packages', '.vs', 'node_modules',
    'dist', 'build', '.idea', '.vscode', 'coverage', 'logs',
    '.gradle', 'target', 'out', 'wwwroot',
}

CONFIG_NAMES        = {'web.config', 'global.asax', 'global.asax.cs', 'app_code'}
ROUTE_CONFIG_NAMES  = {'routeconfig.cs'}


def _should_skip(dir_name: str) -> bool:
    return dir_name.lower() in {s.lower() for s in SKIP_DIRS}


def _read_file(path: str) -> str:
    try:
        # utf-8-sig strips BOM (﻿) present in many Visual Studio .cs/.aspx files
        # so the first ^using/^namespace regex anchors match correctly
        return Path(path).read_text(encoding='utf-8-sig', errors='replace')
    except Exception:
        return ''


def discover_paths(repo_path: str, max_pages: int = 5000) -> Dict[str, List[dict]]:
    """
    Walk repo_path and collect file paths without reading content.

    Returns:
        dict with keys: pages, controls, masters, configs, cs_files
        Each value is a list of path dicts: {path, name, filename, rel_path}
    """
    result = {'pages': [], 'controls': [], 'masters': [], 'configs': [], 'cs_files': [], 'routes': []}
    repo = Path(repo_path)
    page_count = 0

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not _should_skip(d)]

        for fname in files:
            fpath = Path(root) / fname
            fname_lower = fname.lower()

            try:
                rel = str(fpath.relative_to(repo))
            except ValueError:
                rel = fname

            rec = {
                'path': str(fpath),
                'name': Path(fname).stem,
                'filename': fname,
                'rel_path': rel,
            }

            if fname_lower in CONFIG_NAMES or fname_lower == 'web.config':
                result['configs'].append(rec)
            elif fname_lower in ROUTE_CONFIG_NAMES:
                result['routes'].append(rec)
            elif fname_lower.endswith('.aspx') and not fname_lower.endswith('.aspx.cs'):
                if page_count < max_pages:
                    result['pages'].append(rec)
                    page_count += 1
            elif fname_lower.endswith('.ascx') and not fname_lower.endswith('.ascx.cs'):
                result['controls'].append(rec)
            elif fname_lower.endswith('.master') and not fname_lower.endswith('.master.cs'):
                result['masters'].append(rec)
            elif fname_lower.endswith('.cs'):
                result['cs_files'].append(rec)

    return result


def build_codebehind_map(paths: Dict[str, List[dict]]) -> Dict[str, str]:
    """
    Build a map of aspx_path_lower -> cs_path for code-behind lookups.
    Handles both {file}.aspx.cs and {file}.cs naming conventions.
    """
    cb_map: Dict[str, str] = {}
    for rec in paths['cs_files']:
        p = rec['path'].lower()
        # .aspx.cs → maps to .aspx
        if p.endswith('.aspx.cs'):
            cb_map[p[:-3]] = rec['path']  # strip .cs → .aspx
        elif p.endswith('.ascx.cs'):
            cb_map[p[:-3]] = rec['path']
        elif p.endswith('.master.cs'):
            cb_map[p[:-3]] = rec['path']
        # Also map by stem (fallback for same-folder, same-name .cs)
        cb_map[p] = rec['path']
    return cb_map


def load_aspx_repo(repo_path: str, max_pages: int = 5000) -> Dict[str, list]:
    """
    Full load: discover paths then read and return file records.

    Each record has: path, name, filename, rel_path, content, codebehind_content
    Raw content is included so parsers can extract metadata.
    After parsing, callers should NOT store raw content in the index.

    Args:
        repo_path:  Root directory of the repository.
        max_pages:  Cap on .aspx page count (controls/masters uncapped).

    Returns:
        dict with keys: pages, controls, masters, configs
    """
    repo_path = str(Path(repo_path).resolve())

    print(f"  Discovering files in: {repo_path}")
    paths = discover_paths(repo_path, max_pages)
    cb_map = build_codebehind_map(paths)

    print(f"  Found: {len(paths['pages'])} .aspx | {len(paths['controls'])} .ascx | "
          f"{len(paths['masters'])} .master | {len(paths['cs_files'])} .cs | "
          f"{len(paths.get('routes', []))} route config(s)")

    def _enrich(rec: dict) -> dict:
        content = _read_file(rec['path'])
        # Try code-behind by full path first, then fallback by path + '.cs'
        cb_path = cb_map.get(rec['path'].lower()) or cb_map.get(rec['path'].lower() + '.cs', '')
        cb_content = _read_file(cb_path) if cb_path else ''
        return {**rec, 'content': content, 'codebehind_content': cb_content}

    # Load pages with progress
    pages = []
    for i, rec in enumerate(paths['pages']):
        if i > 0 and i % 200 == 0:
            print(f"    ... loaded {i}/{len(paths['pages'])} pages")
        pages.append(_enrich(rec))

    controls = [_enrich(r) for r in paths['controls']]
    masters  = [_enrich(r) for r in paths['masters']]

    # Config files
    configs = []
    for rec in paths['configs']:
        content = _read_file(rec['path'])
        configs.append({**rec, 'content': content})

    # Route config files (RouteConfig.cs)
    routes = []
    for rec in paths.get('routes', []):
        routes.append({**rec, 'content': _read_file(rec['path'])})

    return {'pages': pages, 'controls': controls, 'masters': masters, 'configs': configs, 'routes': routes}
