# ASPX Analyzer — Claude Code Agent Skill

Reverse-engineers ASP.NET Web Forms applications (`.aspx`/`.ascx`/`.master`) into a
persistent JSON index, five human-readable views, and — for repos doing a
legacy-to-modern migration — an [OpenSpec](https://github.com/Fission-AI/OpenSpec)
handoff (`config.yaml` + per-capability proposal stubs).

**Doing a legacy modernization with OpenSpec?** See
[openspec_setup.md](openspec_setup.md) for the complete guide — installing OpenSpec,
reverse-engineering a legacy repo into it with this skill, and the day-to-day
Spec-Driven Development loop for building every feature afterward. See
[EXAMPLE_WALKTHROUGH.md](EXAMPLE_WALKTHROUGH.md) for a real, fully-verified run of the
whole thing against a public repo — cloning, analyzing 1147 real pages, setting up
OpenSpec, and modernizing one real capability (legacy Web Forms grid → ASP.NET Core Web
API + React/TypeScript) end to end, every command shown.

---

## What You Get

| # | View | What it covers |
|---|------|----------------|
| 1 | **Project Overview** | Architecture, master pages, auth model, functional areas, component summary |
| 2 | **Page-by-Page** | Every `.aspx` listed with controls, event handlers, redirects, auth — grouped by folder |
| 3 | **Functional View** | Pages grouped by business domain: Authentication, Orders, Admin, Reports, Users, etc. |
| 4 | **Component View** | All `.ascx` user controls and `.master` pages with usage maps |
| 5 | **Navigation Map** | Page-to-page transition graph (HyperLinks + Response.Redirect) |

Plus: `--page <name>` / `--area <name>` deep-dives, a memory-safe streaming mode for
10,000+ file repos ([aspx_business_analyzer.py](.claude/skills/aspx-analyzer/scripts/aspx_business_analyzer.py)),
and the OpenSpec emitter ([aspx_openspec_emitter.py](.claude/skills/aspx-analyzer/scripts/aspx_openspec_emitter.py)).

No API key required — Claude Code is the AI engine; the Python scripts only do
deterministic static parsing.

---

## Requirements

| Tool | Version |
|------|---------|
| Claude Code | any current version |
| Python | 3.8 or later |
| Git | any version, on PATH (only needed for GitHub-URL targets) |
| [OpenSpec CLI](https://github.com/Fission-AI/OpenSpec) | only if you want the OpenSpec handoff |

Pure standard library — no `pip install` needed for the analyzer itself
([.claude/skills/aspx-analyzer/assets/requirements.txt](.claude/skills/aspx-analyzer/assets/requirements.txt)).

---

## Layout

This is a **project-level Claude Code Agent Skill** — Claude Code auto-discovers it
from `.claude/skills/`, no registration step required.

```
your-project/
└── .claude/
    └── skills/
        └── aspx-analyzer/
            ├── SKILL.md              ← playbook Claude Code reads when triggered
            ├── assets/requirements.txt
            └── scripts/
                ├── aspx_analysis_skill.py       (5-view analyzer, JSON index)
                ├── aspx_business_analyzer.py    (streaming mode, huge repos)
                ├── aspx_openspec_emitter.py     (index.json -> openspec/ handoff)
                ├── aspx_roadmap_emitter.py      (index.json -> MODERNIZATION_ROADMAP.md)
                ├── aspx_stakeholder_doc_emitter.py (index.json -> STAKEHOLDER_DOCUMENTATION.md)
                └── engine/                      (loader/parser/indexer/reporter)
```

Commit `.claude/skills/aspx-analyzer/` to your repo — every teammate gets it on
`git pull`, no per-developer setup.

---

## Usage

Open the target project in Claude Code and just ask, in plain language:

```
Analyze the ASPX pages in this repo
Reverse engineer https://github.com/org/WebFormsApp
Show me the functional view
Deep dive on the Checkout page
What pages are in the Administration area?
```

Claude Code matches these against the `description` in
[.claude/skills/aspx-analyzer/SKILL.md](.claude/skills/aspx-analyzer/SKILL.md) and runs
the analyzer for you — asks for target + view if you didn't specify one, builds the
JSON index on first run, re-uses the cached index on every follow-up.

### Running the scripts directly (no Claude Code)

```bash
# Analyze a GitHub repository
python .claude/skills/aspx-analyzer/scripts/aspx_analysis_skill.py \
    https://github.com/org/MyWebFormsApp --view project --save-report

# Analyze the current directory
python .claude/skills/aspx-analyzer/scripts/aspx_analysis_skill.py \
    . --view project --save-report

# Huge repo (10,000+ files) — streaming, single consolidated business report
python .claude/skills/aspx-analyzer/scripts/aspx_business_analyzer.py . --workers 8
```

All views/flags (`--view`, `--page`, `--area`, `--rebuild`, `--output`,
`--save-report`) are documented in the SKILL.md playbook and the scripts' own
`--help`.

---

## OpenSpec Handoff (modernization workflow)

If you're planning the legacy → modern rewrite with
[OpenSpec](https://github.com/Fission-AI/OpenSpec), the order of operations is below.
For the full walkthrough — installing OpenSpec, day-to-day SDD commands, config.yaml
customization, troubleshooting — see **[openspec_setup.md](openspec_setup.md)**.

```bash
# 1. One-time, scaffolds openspec/{specs,changes,config.yaml} + its own .claude/skills/
openspec init --tools claude

# 2. Reverse-engineer the legacy repo (builds/reuses the JSON index) — via Claude Code
#    chat ("analyze this repo") or directly:
python .claude/skills/aspx-analyzer/scripts/aspx_analysis_skill.py . --view project --save-report

# 3. Project the index into the OpenSpec workspace
python .claude/skills/aspx-analyzer/scripts/aspx_openspec_emitter.py \
    ./MyApp/MyApp_aspx_index.json --openspec-dir ./openspec
```

Step 3 writes:
- **`openspec/config.yaml`** — `context:` (stack, auth model, capability inventory,
  direct-SQL debt) and `rules:` (modernization constraints — preserve discovered
  auth roles, flag direct-SQL pages for migration, require legacy page references
  in proposals). Written inside a marked auto-generated block; re-running only
  refreshes that block and never touches anything else you've added to the file.
- **`openspec/changes/<area-slug>/proposal.md`** — one stub per functional
  area/capability (`## Why` / `## What Changes` / `## Impact`), pre-filled with the
  legacy page list, purpose, auth, and data-access facts for that capability.
  Existing proposal files are never overwritten — the emitter only fills in the
  ones that don't exist yet, so you can safely re-run it after adding more pages.

You (or OpenSpec's own proposal workflow) then flesh out `## What Changes` /
`## Impact` per capability — the emitter gives you a factual starting point drawn
from the actual legacy code, not the finished proposal.

---

## Modernization Roadmap (tech-stack setup + build order)

Standalone — doesn't require OpenSpec. Answers "how do I even set up the target stack"
and "what order do I build things in":

```bash
python .claude/skills/aspx-analyzer/scripts/aspx_roadmap_emitter.py \
    ./MyApp/MyApp_aspx_index.json --stack dotnet-webapi-react
```

Writes `MODERNIZATION_ROADMAP.md` with:
- **Target stack setup** — real folder layout + real scaffold commands
  (`dotnet new webapi`, `npm create vite@latest`, ...) for the chosen stack.
  `--list-stacks` shows all available (`dotnet-webapi-react`, `dotnet-razor-pages`).
- **Build order** — every functional area ranked simplest-first by an explicit
  complexity score (direct-SQL pages weighted heaviest — that's the dominant migration
  cost, not the UI port), each with one concrete "port this page first" suggestion.

Both the stack and the ranking logic are verified against a real migration in
[EXAMPLE_WALKTHROUGH.md](EXAMPLE_WALKTHROUGH.md), not just designed on paper.

---

## Stakeholder Documentation (business-facing overview)

For a non-technical audience — one document that explains the existing legacy app,
where modernization stands, where to start, and how the complete project gets built:

```bash
python .claude/skills/aspx-analyzer/scripts/aspx_stakeholder_doc_emitter.py \
    ./MyApp/MyApp_aspx_index.json --openspec-dir ./openspec
```

`--openspec-dir` is optional — omit it if no OpenSpec workspace exists yet; the doc
still generates, reporting modernization status as "not started." No `openspec` CLI
install required either way — progress is read directly from `openspec/changes/*/tasks.md`.

Writes `STAKEHOLDER_DOCUMENTATION.md` with:
- **Executive Summary** — real page/control/master counts, capability count, auth
  model, direct-SQL risk count, unknown-auth gap count.
- **Business Capability Inventory** — every functional area with page count,
  data-access risk, and relative complexity.
- **Current Modernization Status** — real per-capability OpenSpec task progress, or
  "not started" if none exists.
- **Getting Started** — the single lowest-risk capability and its concrete first
  page to port (same ranking the roadmap emitter uses — imported, not duplicated,
  so the two documents never disagree).
- **How to Build the Complete Project, End to End** — the SDD loop stated once,
  generically, applying to every remaining capability.
- **Quality & Governance Controls** — the review-gate/verification rules this
  project's process enforces, in plain language.

---

## What Gets Parsed

- **`.aspx`** — `<%@ Page %>` directive, `<%@ Register %>`, all `<asp:*>` controls,
  data sources, AJAX (`ScriptManager`/`UpdatePanel`), HTML/`HyperLink` navigation,
  named-route resolution via `RouteConfig.cs`
- **`.aspx.cs`** — namespace/class, `Page_Load`/`Page_Init`, event handlers,
  `Response.Redirect`/`Server.Transfer`, direct-SQL detection, auth attributes
  (`[Authorize]`, `User.IsInRole`, `Request.IsAuthenticated`)
- **`.ascx`** — class, public properties, controls contained, events raised
- **`.master`** — content placeholders, nav/login controls, AJAX presence
- **`web.config`** — auth mode, forms login URL, connection string names,
  `<location>` rules, session mode, custom errors, SMTP host

Full auth-inference and functional-area-keyword tables are in
[SKILL.md](.claude/skills/aspx-analyzer/SKILL.md).

---

## Performance

Both `aspx_analysis_skill.py` and `aspx_business_analyzer.py` build their index
through the same streaming engine ([engine/aspx_stream.py](.claude/skills/aspx-analyzer/scripts/engine/aspx_stream.py)):
paths are discovered first (no content read), then each file is read, parsed,
and its raw content discarded — one at a time per worker — so peak memory
stays flat regardless of repo size. Parsing is parallelized across processes
by default (`--workers`, CPU count capped at 8; `--workers 1` forces serial).
There is no hard page cap (`--max-pages 0` = unlimited).

| Repo size | Index build | Follow-up queries |
|-----------|-------------|-------------------|
| ~50 pages | < 5 seconds | instant |
| ~300 pages | ~10 seconds | instant |
| ~1000 pages | ~20-30 seconds (parallel) | instant |
| ~3000 pages | ~1 minute (parallel) | instant |
| 10,000+ pages | minutes, flat memory — use `--workers 8`; `aspx_business_analyzer.py` for a single consolidated report instead of 5 | instant |

The JSON index is built once (`{repo}_aspx_index.json` / `{repo}_business_index.json`);
every later `--page`/`--area`/`--view` or OpenSpec emitter run reads from it — no
source files re-read. Use `--rebuild` after source changes. Index files are
saved compact (no indentation) once a repo passes ~500 pages, since at that
size the index is read by tooling, not humans, and pretty-printing roughly
doubles file size and save time.

---

## Troubleshooting

**"No ASPX files found"** — confirm the target is Web Forms (not MVC/Blazor/Razor
Pages) and that `.aspx` files exist under the target path.

**Skill doesn't trigger in Claude Code** — confirm the folder is at
`.claude/skills/aspx-analyzer/SKILL.md` (not `.github/skills/`, which is the
GitHub Copilot convention and is not read by Claude Code).

**`aspx_openspec_emitter.py` errors "openspec dir does not exist"** — run
`openspec init --tools claude` in the target repo first; the emitter only fills
content into an existing `openspec/` scaffold, it never creates one.

**Python not found** — `python --version`, then try `python3 --version`; install
from https://python.org if neither works.

**Index is stale after code changes** —
```bash
python .claude/skills/aspx-analyzer/scripts/aspx_analysis_skill.py . --rebuild --view project
```
