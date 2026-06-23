"""
Streaming ASPX Indexer  (10,000+ file safe)
===========================================
Memory-safe replacement for load_aspx_repo + build_index when the repo is huge.

Why the old path hangs / kills PowerShell:
  * load_aspx_repo() reads EVERY file's raw content into in-memory lists
    (pages/controls/masters each holding full `content` + `codebehind_content`)
    BEFORE parsing — peak memory ≈ whole repo in RAM.
  * the whole JSON index then holds it all again.

This module instead STREAMS: discover paths only, then process one file at a
time (read → parse → keep compact dict → discard raw text). At most one file
body is alive per worker. Optional multiprocessing fans the parse out across
cores; workers return small dicts so memory stays bounded regardless of repo
size.

Public:
    build_index_streaming(repo_path, repo_name, workers=0,
                          max_bytes=1_500_000, max_pages=0, progress=True)
        -> compact index dict (same shape the reporters expect, plus
           per-page 'methods' for the business report)
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ProcessPoolExecutor

from engine.aspx_loader import discover_paths, build_codebehind_map, _read_file
from engine.aspx_parser import (
    parse_aspx_page, parse_ascx_control, parse_master_page, parse_web_config,
)
from engine.aspx_method_extractor import extract_methods
from engine.aspx_indexer import (
    _link_usages, _parse_route_configs, _build_navigation_map,
    _build_functional_areas, _build_component_map, _auth_breakdown,
)

# generated / designer / minified files never carry business logic
_SKIP_CB_SUFFIX = ('.designer.cs', '.g.cs', '.g.i.cs', 'assemblyinfo.cs')


def _skip_cb(path: str) -> bool:
    p = path.lower()
    return any(p.endswith(s) for s in _SKIP_CB_SUFFIX)


# ---------------------------------------------------------------------------
# Worker — runs in a separate process (must be top-level & picklable)
# ---------------------------------------------------------------------------

def _process_page(args):
    """Read one .aspx (+ code-behind), return compact parsed dict + methods."""
    rec, cb_path, max_bytes = args
    try:
        if os.path.getsize(rec['path']) > max_bytes:
            content = _read_file(rec['path'])[:max_bytes]
        else:
            content = _read_file(rec['path'])
    except OSError:
        content = ''

    cb_content = ''
    if cb_path and not _skip_cb(cb_path):
        try:
            if os.path.getsize(cb_path) <= max_bytes:
                cb_content = _read_file(cb_path)
        except OSError:
            cb_content = ''

    parsed = parse_aspx_page({**rec, 'content': content,
                              'codebehind_content': cb_content})
    parsed['methods'] = extract_methods(cb_content)
    return parsed


def _process_simple(args):
    """Generic worker for .ascx / .master (no method extraction needed)."""
    rec, cb_path, kind, max_bytes = args
    content = ''
    try:
        if os.path.getsize(rec['path']) <= max_bytes:
            content = _read_file(rec['path'])
    except OSError:
        pass
    cb_content = ''
    if cb_path and not _skip_cb(cb_path):
        try:
            if os.path.getsize(cb_path) <= max_bytes:
                cb_content = _read_file(cb_path)
        except OSError:
            pass
    full = {**rec, 'content': content, 'codebehind_content': cb_content}
    return parse_ascx_control(full) if kind == 'ascx' else parse_master_page(full)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def build_index_streaming(repo_path: str, repo_name: str,
                          workers: int = 0, max_bytes: int = 1_500_000,
                          max_pages: int = 0, progress: bool = True) -> dict:
    repo_path = str(Path(repo_path).resolve())
    if progress:
        print(f"  Discovering files (streaming, memory-safe) in: {repo_path}")

    cap = max_pages if max_pages > 0 else 1_000_000
    paths = discover_paths(repo_path, max_pages=cap)
    cb_map = build_codebehind_map(paths)

    n_pages = len(paths['pages'])
    n_ctrls = len(paths['controls'])
    n_mast  = len(paths['masters'])
    if progress:
        print(f"  Found: {n_pages} .aspx | {n_ctrls} .ascx | {n_mast} .master | "
              f"{len(paths['cs_files'])} .cs | {len(paths.get('routes', []))} route cfg")

    def _cb_for(rec):
        lp = rec['path'].lower()
        return cb_map.get(lp) or cb_map.get(lp + '.cs', '')

    page_args = [(r, _cb_for(r), max_bytes) for r in paths['pages']]
    ctrl_args = [(r, _cb_for(r), 'ascx', max_bytes) for r in paths['controls']]
    mast_args = [(r, _cb_for(r), 'master', max_bytes) for r in paths['masters']]

    pages: List[dict] = []
    controls: List[dict] = []
    masters: List[dict] = []

    if workers and workers > 1 and n_pages > 200:
        if progress:
            print(f"  Parsing pages across {workers} processes ...")
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for i, p in enumerate(ex.map(_process_page, page_args, chunksize=25)):
                pages.append(p)
                if progress and (i + 1) % 500 == 0:
                    print(f"    ... {i + 1}/{n_pages} pages")
            controls = list(ex.map(_process_simple, ctrl_args, chunksize=25))
            masters  = list(ex.map(_process_simple, mast_args, chunksize=25))
    else:
        if progress:
            print(f"  Parsing {n_pages} pages (single process, streaming) ...")
        for i, a in enumerate(page_args):
            pages.append(_process_page(a))
            if progress and (i + 1) % 500 == 0:
                print(f"    ... {i + 1}/{n_pages} pages")
        controls = [_process_simple(a) for a in ctrl_args]
        masters  = [_process_simple(a) for a in mast_args]

    # web.config
    web_config: dict = {}
    for cfg in paths['configs']:
        if cfg.get('filename', '').lower() == 'web.config':
            web_config = parse_web_config({**cfg, 'content': _read_file(cfg['path'])})
            break

    if progress:
        print("  Building cross-references ...")
    _link_usages(pages, controls, masters)

    route_records = [{**r, 'content': _read_file(r['path'])}
                     for r in paths.get('routes', [])]
    route_map = _parse_route_configs(route_records, pages)

    nav_map          = _build_navigation_map(pages, route_map)
    functional_areas = _build_functional_areas(pages)
    component_map    = _build_component_map(controls, masters)

    _VAL = {'requiredfieldvalidator', 'rangevalidator', 'comparevalidator',
            'regularexpressionvalidator', 'customvalidator'}
    stats = {
        'total_pages': n_pages, 'total_controls': n_ctrls, 'total_masters': n_mast,
        'total_functional_areas': len(functional_areas),
        'total_named_routes': len(route_map),
        'pages_with_ajax': sum(1 for p in pages if p.get('uses_ajax')),
        'pages_with_sql_direct': sum(1 for p in pages if p.get('uses_sql_direct')),
        'pages_with_master': sum(1 for p in pages if p.get('master_page')),
        'pages_with_codebehind': sum(1 for p in pages if p.get('class_name')),
        'pages_with_validators': sum(
            1 for p in pages
            if any(c['type'] in _VAL for c in p.get('form_controls', []))),
        'total_methods': sum(len(p.get('methods', [])) for p in pages),
        'total_stored_procs': len({sp for p in pages for m in p.get('methods', [])
                                   for sp in m.get('stored_procs', [])}),
        'auth_breakdown': _auth_breakdown(pages),
        'functional_area_counts': {a: len(v) for a, v in functional_areas.items()},
    }

    return {
        'project': repo_name, 'repo_path': repo_path,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'stats': stats, 'web_config': web_config,
        'pages': pages, 'user_controls': controls, 'master_pages': masters,
        'functional_areas': functional_areas, 'navigation_map': nav_map,
        'component_map': component_map, 'route_map': route_map,
    }
