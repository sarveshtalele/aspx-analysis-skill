---
name: aspx-analyzer
description: >
  Analyze ASP.NET Web Forms applications (.aspx pages, .ascx user controls, .master pages).
  Produces 5 views: (1) Project Overview — architecture, master pages, auth model, functional areas;
  (2) Page-by-Page — every .aspx with controls, handlers, redirects; (3) Functional View — pages
  grouped by business domain (Authentication, Orders, Admin, Reports, etc.); (4) Component View —
  user controls and master pages with usage maps; (5) Navigation Map — page-to-page transition graph.
  Supports GitHub repo URLs AND local/current repo paths. Builds a JSON index once; subsequent
  queries served from cache — handles 1000+ ASPX pages efficiently.
  For HUGE repos (10,000+ files) use the streaming single-file business analyzer
  (aspx_business_analyzer.py) — memory-safe, multiprocess, emits ONE consolidated
  business-logic markdown file instead of 5.
  Trigger when user says: analyze aspx, aspx pages, web forms analysis, page inventory,
  aspx architecture, what pages does this app have, show me the screen flow, show user controls,
  master page analysis, aspx functional view, reverse engineer aspx, analyze this aspx project,
  how does this web forms app work, what is on the Login page, show me the Admin area pages,
  or provides any GitHub URL for an ASP.NET Web Forms project.
version: "1.0.0"
tools:
  - run_in_terminal
  - read_file
  - create_file
  - insert_edit_into_file
  - file_search
  - grep_search
---

# ASP.NET Web Forms Application Analyzer

You are a senior .NET architect performing a complete analysis of an ASP.NET Web Forms application.
**You are the AI engine.** The Python script does static parsing; you provide architectural insight,
business-domain explanation, and professional narrative.

The analysis produces **5 views** from a single persistent JSON index:
1. **Project Overview** — architecture, master pages, auth, functional areas
2. **Page-by-Page** — every .aspx page with controls, handlers, redirects
3. **Functional View** — pages grouped by business domain
4. **Component View** — user controls + master pages catalog
5. **Navigation Map** — page transition graph

---

## ⚡ Large-Repo Fast Mode (10,000+ files) — USE THIS FIRST for big/legacy apps

The original 5-view path reads every file into memory, prints the whole report to
stdout, and writes 5 MD files + a large JSON. On 10,000+ file repos that exhausts
memory and **PowerShell / the terminal gets terminated**, and the AI then chokes
reading 5 big files.

For big repos run the **streaming single-file business analyzer** instead. It:
- **Streams** files one at a time (read → parse → keep compact dict → discard raw
  text). Peak memory stays flat regardless of repo size.
- Runs the parse across **multiple processes** (`--workers`).
- **Skips** generated/`.designer.cs`/minified files and caps per-file bytes.
- Prints only a **short summary** to stdout (no flood → no hang).
- Emits **ONE** `{repo}_BusinessAnalysis.md` (business impact + website-flow view +
  per-method business logic in the client format) plus one compact JSON index.

### Run it

```bash
# Whole project — one consolidated business file
python scripts/aspx_business_analyzer.py . --workers 8

# GitHub repo
python scripts/aspx_business_analyzer.py https://github.com/org/App --workers 8

# Deep per-method detail for ONE capability (keeps output focused)
python scripts/aspx_business_analyzer.py . --detail-area Orders --full-detail
```

Key options: `--workers N` (parallel; default = CPU count, cap 8; `1` = serial),
`--max-bytes N` (skip code-behind larger than N), `--max-pages N` (cap pages),
`--detail-area A` / `--full-detail` (per-method detail scope), `--max-files N`
(detailed-logic page cap, default 40), `--rebuild`, `--output DIR`.

### Consolidated report sections (matches the client spec)
1. Executive Business Summary & **Business Impact**
2. Application Snapshot (metrics)
3. **How the Business Works — Website View** (capability map, entry points, user journeys)
4. Business Capabilities in Detail (rules, DB routines, data-touching pages)
5. **Detailed Business Logic** per File → Class → Method → Purpose → Detailed
   Business Logic → Validation/Conditional Rules → Called Components/Dependencies →
   Data Flow/Mappings
6. Data Architecture, Integrations & Access Control
7. Risks & Modernization Notes

After it finishes, **read the single `{repo}_BusinessAnalysis.md`** and add senior-
architect narrative on top. Do NOT read the JSON index in full on huge repos —
query it selectively or re-run with `--detail-area` for a specific capability.

---

## Step 1 — Identify Target

Ask the user (or infer from context):

> **"What should I analyze?"**
> 1. A GitHub repository URL — e.g. `https://github.com/org/WebFormsApp`
> 2. A local path — e.g. `C:\Projects\MyApp` or `/home/user/webapp`
> 3. The **current repository** — type `.` or just say "this repo" / "current project"

If the user provides a GitHub URL, use it directly.
If the user says "this repo", "current project", "analyze this", "analyze here", or similar,
use `.` (current working directory) as the target.

---

## Step 2 — Ask for View Type

> **"What view do you want?"**
> 1. **Project Overview** — architecture, stats, master pages, auth model, functional areas *(recommended first run)*
> 2. **Page-by-Page** — every .aspx page in detail (grouped by folder)
> 3. **Functional View** — pages grouped by business function (Auth / Admin / Orders / etc.)
> 4. **Component View** — master pages and user controls catalog
> 5. **Specific page** — deep-dive one page (e.g. "Login", "ProductList")
> 6. **Specific area** — all pages in one functional area (e.g. "Administration", "Orders")
> 7. **Navigation Map** — page-to-page transition map

If the user has already stated what they want, skip this question.

Map user intent → CLI flags:
- "overview" / "project" / "architecture"    → `--view project`
- "all pages" / "page by page" / "pages"     → `--view pages`
- "functional" / "by function" / "business"  → `--view functional`
- "controls" / "components" / "user controls"→ `--view component`
- "navigation" / "flow" / "links"            → `--view navigation`
- "show me the Login page"                   → `--page Login`
- "show me the Admin area"                   → `--area Administration`
- "tell me about Orders"                     → `--area Orders`

---

## Step 3 — Check for Cached Index

Before running the script, check if a JSON index already exists:

```bash
# For GitHub URL — check after clone
ls {repo_name}/{repo_name}_aspx_index.json 2>/dev/null

# For local path
ls {repo_name}_aspx_index.json 2>/dev/null
# or check the output folder
```

If the index exists and the user did NOT say "rebuild" or "re-index", add **no extra flags** (the
script automatically loads the cached index).

If the user says "rebuild", "re-parse", "fresh analysis", or "update index" → add `--rebuild`.

---

## Step 4 — Run the Analysis Script

The script is at:
```
.github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py
```

**Check Python:**
```bash
python --version
```

**Run the script** — substitute `<TARGET>` and flags from Steps 1-3:

```bash
# GitHub URL
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    https://github.com/org/repo --view project --save-report

# Local path
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    C:\Projects\MyApp --view project --save-report

# Current repo (use absolute path of CWD)
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    . --view project --save-report

# Specific page
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    . --page Login --save-report

# Specific area
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    . --area Administration --save-report

# Re-query from cache (fast, no re-parse)
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    . --view functional
```

**Always add `--save-report`** so you can read the report file in Step 5.

Wait for the script to complete. It prints progress every 200 pages.

Output produced:
| File | Description |
|------|-------------|
| `{repo}_aspx_index.json` | **Persistent index — cached for future queries** |
| `{repo}_aspx_project.md` | Project overview report |
| `{repo}_aspx_pages.md` | Page-by-page report |
| `{repo}_aspx_functional.md` | Functional view report |
| `{repo}_aspx_component.md` | Component catalog |
| `{repo}_aspx_page_{name}.md` | Specific page deep-dive |
| `{repo}_aspx_area_{name}.md` | Specific area deep-dive |

---

## Step 5 — Read the Generated Data

Read the saved report:
```
{output_dir}/{repo_name}_aspx_{view}.md
```

Also read the JSON index for additional context:
```
{output_dir}/{repo_name}_aspx_index.json
```

Key index sections:
- `stats` — total counts, auth breakdown, functional area counts
- `web_config` — auth mode, connection strings, session mode
- `pages[]` — per-page metadata: controls, handlers, redirects, auth, purpose
- `user_controls[]` — per-control metadata with `used_by_pages` list
- `master_pages[]` — per-master with `content_placeholders` and `used_by_pages`
- `functional_areas` — `{area: [{name, rel_path, purpose, auth}]}`
- `navigation_map` — `{page_path: [target_paths]}`

---

## Step 6 — Provide AI Analysis

Based on the parsed data, deliver professional architectural insight.
Think like a senior .NET architect who has read the entire codebase.

### 6a · For Project Overview view

**Executive Summary** (2-3 sentences):
- What does this Web Forms application do and for whom?
- What is its technical architecture? (e.g. "Multi-tier Web Forms app with master page layout,
  code-behind pattern, Forms Authentication, and SqlDataSource-driven data binding")
- Top 3 observations about maintainability or technical debt

**Architecture Assessment:**
- Master page strategy (single vs. multiple templates, role-specific layouts)
- Code-behind pattern usage vs. presentation logic separation
- Data access pattern: ORM / DataSets / Direct SQL / mixed
- AJAX strategy: classic UpdatePanel vs. modern patterns
- Authentication model: Forms Auth / Windows Auth / custom

**Functional Area Summary:**
- For each area, 2-3 sentences on what it does and how pages relate
- Identify the main user journeys (e.g. "Customer: Browse → Cart → Checkout → Confirmation")

**Technical Debt Observations:**
- Direct SQL usage (SqlConnection in code-behind = tight coupling, security risk)
- Missing master pages (inconsistent layout)
- Large pages with many controls (God pages)
- Auth gaps (sensitive pages without auth checks)

### 6b · For Page-by-Page view

For each folder/section, provide a brief narrative:
- What is the purpose of this folder? What business capability does it cover?
- Which pages are the most complex? (many controls, many handlers)
- Which pages are entry points vs. intermediate vs. terminal in a workflow?

For standout pages (complex, critical, or unusual), add a paragraph of explanation.

### 6c · For Functional view

For each functional area:
1. **What business process does this area serve?**
2. **User journey:** trigger → steps → completion (name actual pages)
3. **Key pages** and what each does
4. **Auth model** for this area (who can access?)
5. **Integration points** (data sources, external calls detected)

### 6d · For Component view

For each master page:
- What is its purpose? Who uses it (authenticated vs. public)?
- What shared navigation / login controls does it provide?
- Content placeholder strategy

For top user controls (by usage count):
- What UI responsibility do they encapsulate?
- Why is this a control rather than inline markup?
- Which pages depend on it?

### 6e · For specific page view

Full analysis:
1. **Purpose** — what user action does this page serve?
2. **UI Layout** — what does the user see? (infer from controls)
3. **Interactions** — what can the user do? (buttons, forms)
4. **Data** — what data is displayed/collected? (grids, data sources, form fields)
5. **Auth** — who can access this page?
6. **Code-Behind Logic** — what business operations happen? (Page_Load, handlers)
7. **Navigation** — how does the user reach this page? Where can they go next?
8. **Technical notes** — any patterns, concerns, or noteworthy implementation details

### 6f · For functional area view

1. **Business Process** — what real-world workflow does this area implement?
2. **Page flow walkthrough** — step-by-step user journey through the actual pages
3. **Key business rules** — what validations or constraints are enforced?
4. **Auth model** — who can access which pages in this area?
5. **Data architecture** — what data entities are involved?
6. **Integration points** — external systems, APIs, email, payment, etc.

---

## Step 7 — Handle Follow-up Queries

The JSON index is persistent. When the user asks follow-up questions:

- "Show me the Login page" → run `--page Login` (fast, uses cached index)
- "What pages are in Admin?" → run `--area Administration`
- "Show me all the reports" → run `--area Reports`
- "What user controls are used?" → run `--view component`
- "How do pages link together?" → run `--view navigation`
- "Rebuild after my changes" → add `--rebuild` flag

**Do NOT re-run with full parse** for follow-up queries — the index is already built.
Just run the script with the new `--page` or `--area` flag and `--save-report`.

---

## Step 8 — Report Completion

```
ASPX Analysis complete ✓
Target     : {target}
Index      : {index_path}   (cached — re-use for follow-up queries)
Report     : {report_path}

Stats:
  Pages   : {N} | Controls : {N} | Masters : {N}
  Areas   : {functional_areas list}
  Auth    : {auth_breakdown}

Available views:
  --view project      Architecture overview
  --view pages        All {N} pages by folder
  --view functional   Pages by business function
  --view component    {N} controls + {N} master pages
  --view navigation   Page navigation map
  --page <name>       Any specific page deep-dive
  --area <name>       Any functional area deep-dive
```

---

## Manual Fallback (Script Not Found)

If the script cannot be found or Python is unavailable:

1. Search for ASPX files: `*.aspx`, `*.ascx`, `*.master`, `web.config`
2. For each `.aspx`, read: the `<%@ Page %>` directive, all `<asp:*>` controls,
   code-behind class name and event handlers, `Response.Redirect` calls
3. Group pages by folder — folders indicate functional areas
4. Use the template structure from Step 6 to deliver the analysis

---

## Notes

- **No API key required** — Claude Code is the AI engine
- **Cached index** — 1000+ page repos are parsed once; follow-up queries are instant
- **Local repo support** — pass `.` to analyze the current working directory
- **GitHub URL support** — shallow-clones the repo, parses, then removes the clone
- **ASPX-only** — focused on Web Forms; does not parse MVC Razor views or Blazor
- **Web.config** — extracts auth mode, Forms Auth login URL, connection strings,
  location access rules, session mode, custom errors
- **Code-behind** — extracts namespace, class, event handlers, imports, redirects
- **Auth inference** — [Authorize], User.IsInRole, Request.IsAuthenticated, folder heuristics
- **Functional area detection** — keyword matching on page name + folder path + imports
