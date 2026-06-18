# ASPX Analysis Skill — Install & Usage Guide

A GitHub Copilot Agent Skill that fully analyzes ASP.NET Web Forms applications.
Works from a **GitHub URL** or directly on your **local / current repository**.
Parses 1000+ `.aspx` pages efficiently by building a persistent JSON index once — all follow-up queries are instant.

---

## What You Get

Five on-demand views of any Web Forms application:

| # | View | What it covers |
|---|------|----------------|
| 1 | **Project Overview** | Architecture, master pages, auth model, functional areas, component summary |
| 2 | **Page-by-Page** | Every `.aspx` listed with controls, event handlers, redirects, auth — grouped by folder |
| 3 | **Functional View** | Pages grouped by business domain: Authentication, Orders, Admin, Reports, Users, etc. |
| 4 | **Component View** | All `.ascx` user controls and `.master` pages with usage maps |
| 5 | **Navigation Map** | Page-to-page transition graph (HyperLinks + Response.Redirect) |

Plus two targeted deep-dives:

- **`--page <name>`** — complete analysis of one specific `.aspx` page
- **`--area <name>`** — all pages in one functional area with full detail

No API key required. GitHub Copilot is the AI engine.

---

## Requirements

| Tool | Version |
|------|---------|
| VS Code | 1.90 or later |
| GitHub Copilot Chat extension | latest |
| Python | 3.8 or later |
| Git | any version, must be on PATH |

---

## Installation (one-time, 2 minutes)

### Step 1 — Copy the skill folder into your project

```
Your project/
└── .github/
    └── skills/
        └── aspx-analysis-skill/   ← paste this folder here
```

If `.github/skills/` does not exist yet, create it.

Your final structure:
```
.github/
└── skills/
    └── aspx-analysis-skill/
        ├── SKILL.md
        ├── assets/
        │   └── requirements.txt
        └── scripts/
            ├── aspx_analysis_skill.py
            └── engine/
                ├── __init__.py
                ├── aspx_loader.py
                ├── aspx_parser.py
                ├── aspx_indexer.py
                └── aspx_reporter.py
```

### Step 2 — Verify Python is installed

```bash
python --version
# Should print Python 3.8 or higher
```

No third-party packages required — only Python standard library.

### Step 3 — Done. Open Copilot Chat and use the skill.

---

## Connecting to GitHub Copilot Chat

### How Copilot discovers the skill

GitHub Copilot Agent Mode automatically scans the `.github/skills/` folder in your workspace for
`SKILL.md` files. When it finds one, it reads the `description` field to learn the skill's trigger
phrases. No registration step is required.

**Requirements for auto-discovery:**
- The skill folder must be inside `.github/skills/` at the **workspace root**
- The `SKILL.md` file must be present at the top level of the skill folder
- Copilot Chat must be open in **Agent Mode** (`@workspace` or the agent panel)

### Step-by-step: activating the skill in VS Code

1. Open your project in VS Code
2. Open GitHub Copilot Chat with `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Alt+I` (Mac)
3. Switch to **Agent Mode** by clicking the agent icon or typing `@workspace` in the chat input
4. Type any trigger phrase — Copilot will detect the skill and activate it:

```
Analyze the ASPX pages in this repo
```
```
What pages does this Web Forms app have?
```
```
Show me the functional view of this ASP.NET project
```
```
Reverse engineer https://github.com/org/WebFormsApp
```
```
Show me the Login page in detail
```
```
What user controls are used across this project?
```
```
Analyze aspx https://github.com/org/webapp
```

### Full list of trigger phrases

The skill activates on any of these (Copilot matches by intent, not exact wording):

| What you say | What happens |
|---|---|
| `analyze aspx` / `aspx pages` / `web forms analysis` | Project Overview |
| `page inventory` / `what pages does this app have` | Page-by-Page view |
| `aspx architecture` / `show me the screen flow` | Project Overview |
| `functional view` / `pages by function` | Functional View |
| `show user controls` / `component view` | Component View |
| `page navigation` / `how pages link` | Navigation Map |
| `show me the Login page` / `analyze the Checkout page` | Page deep-dive |
| `show me the Admin area` / `what's in Orders` | Area deep-dive |
| GitHub URL for an ASP.NET Web Forms repo | Full project analysis |

---

## How Copilot Uses This Skill

Once activated, Copilot will:

1. **Ask for the target** — GitHub URL, local path, or "this repo" / current directory
2. **Ask for the view** — or infer from your request
3. **Run the Python script** automatically using `run_in_terminal`
4. **Read the generated report and index** to provide AI-quality narrative
5. **Answer follow-up questions** instantly from the cached JSON index (no re-parse needed)

The key insight: **parse once, query many times**. The `{project}_aspx_index.json` is saved to disk.
Every follow-up question (show me page X, what's in area Y) re-uses the cache.

---

## Usage in VS Code Copilot Chat

### Analyze a GitHub repository

```
Analyze aspx https://github.com/org/MyWebFormsApp
```

Copilot will clone, parse, and produce the Project Overview. Then ask for more:

```
Now show me the functional view
```
```
Deep dive on the Checkout page
```
```
What pages are in the Administration area?
```

### Analyze your current (local) repository

Open the project folder in VS Code, then:

```
Analyze the ASPX pages in this project
```

or

```
Show me the page inventory for this repo
```

Copilot uses `.` (current working directory) as the target.

### Ask for a specific page

```
Show me everything about the Login.aspx page
```
```
Analyze the ProductEdit page in detail
```
```
What does the OrderSummary page do?
```

### Ask for a functional area

```
Show all pages in the Admin area
```
```
Walk me through the Orders workflow pages
```
```
What authentication pages does this app have?
```

---

## Where Output Files Land

By default, output goes to `./{project-name}/` in the current directory:

```
your-workspace/
└── MyWebFormsApp/                          ← created automatically
    ├── MyWebFormsApp_aspx_index.json       ← persistent cache  ← re-used for all follow-ups
    ├── MyWebFormsApp_aspx_project.md       ← Project Overview report
    ├── MyWebFormsApp_aspx_pages.md         ← Page-by-Page report
    ├── MyWebFormsApp_aspx_functional.md    ← Functional View report
    ├── MyWebFormsApp_aspx_component.md     ← Component catalog
    ├── MyWebFormsApp_aspx_navigation.md    ← Navigation map
    ├── MyWebFormsApp_aspx_page_Login.md    ← Login page deep-dive (when requested)
    └── MyWebFormsApp_aspx_area_Admin.md    ← Admin area deep-dive (when requested)
```

The `_aspx_index.json` is the most important file — it powers all follow-up queries without
re-parsing the source files.

---

## Running Without Copilot (CLI Only)

### Basic usage

```bash
# Analyze a GitHub repository
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    https://github.com/org/MyWebFormsApp --view project --save-report

# Analyze the current directory
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    . --view project --save-report

# Analyze a local path
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py \
    C:\Projects\MyWebApp --view project --save-report
```

### All views

```bash
# Architecture overview
python ... . --view project

# All pages by folder
python ... . --view pages

# Pages by business function
python ... . --view functional

# User controls + master pages catalog
python ... . --view component

# Page-to-page navigation map
python ... . --view navigation
```

### Specific page or area deep-dives

```bash
# Deep-dive on one page (case-insensitive, partial name match)
python ... . --page Login
python ... . --page ProductEdit
python ... . --page OrderSummary

# Deep-dive on one functional area
python ... . --area Administration
python ... . --area Orders
python ... . --area Authentication
```

### Re-build the cache after source changes

```bash
python ... . --view project --rebuild
```

### Save report to file

```bash
python ... . --view functional --save-report
# Writes to ./{project-name}/{project}_aspx_functional.md
```

### Custom output directory

```bash
python ... https://github.com/org/repo --view project --output C:\Reports --save-report
```

---

## What the Skill Parses

### From `.aspx` pages
- `<%@ Page %>` directive: title, master page, code-behind file, class name
- `<%@ Register %>` directives: which user controls are used
- All `<asp:*>` server controls: type, ID, text (TextBox, Button, GridView, DropDownList, etc.)
- Data source controls: SqlDataSource, ObjectDataSource, EntityDataSource
- AJAX: ScriptManager, UpdatePanel detection
- HTML `<a href>` navigation links
- `<asp:HyperLink NavigateUrl>` links

### From `.aspx.cs` code-behind
- Namespace and class declaration
- `Page_Load`, `Page_Init` presence
- All event handlers: `Button_Click`, `GridView_RowCommand`, `DropDown_SelectedIndexChanged`, etc.
- `Response.Redirect` and `Server.Transfer` targets (navigation out)
- `using` directives (namespace dependencies)
- Direct SQL usage: `SqlConnection`, `SqlCommand` detection
- Auth checks: `[Authorize]`, `User.IsInRole()`, `Request.IsAuthenticated`

### From `.ascx` user controls
- Class, namespace, public properties
- Controls contained, event handlers raised

### From `.master` master pages
- `<asp:ContentPlaceHolder>` IDs
- Navigation controls: `asp:Menu`, `asp:TreeView`, `asp:SiteMapPath`
- Login controls: `asp:Login`, `asp:LoginView`, `asp:LoginStatus`
- ScriptManager (AJAX) presence
- Registered user controls

### From `web.config`
- Authentication mode (Forms / Windows / None)
- Forms auth `loginUrl`
- Connection string names
- `<location>` access rules (allow/deny per path)
- Session mode, custom errors mode, SMTP host

---

## Auth Detection Logic

| Signal | Inferred Auth |
|--------|---------------|
| Page name: login, register, signup, forgotpassword | `anonymous` |
| `[Authorize]` attribute in code-behind | `authenticated` |
| `[Authorize(Roles="Admin")]` | `role:Admin` |
| `User.IsInRole("Manager")` | `role:Manager` |
| `Request.IsAuthenticated` check | `authenticated` |
| Folder path contains `admin/` | `role:Admin` (heuristic) |
| No signals found | `unknown` |

---

## Functional Area Detection

Pages are automatically grouped into areas by matching page name + folder path against keyword lists:

| Area | Keywords matched |
|------|-----------------|
| Authentication | login, logout, register, signup, password, auth, signin |
| Administration | admin, manage, management, dashboard, backoffice |
| Orders | order, cart, checkout, payment, invoice, billing |
| Products | product, catalog, category, inventory, sku |
| Reports | report, statistics, analytics, export, chart |
| Users | user, member, profile, settings, preference |
| Content | article, blog, news, content, cms |
| Search | search, find, browse, filter, results |
| Configuration | config, setting, setup, wizard |
| Errors | error, 404, 500, accessdenied, forbidden |
| Home | home, index, default, landing, welcome |

---

## Performance — Handling 1000+ Pages

| Repo size | Index build time | Follow-up queries |
|-----------|-----------------|-------------------|
| ~50 pages | < 5 seconds | instant |
| ~300 pages | ~15 seconds | instant |
| ~1000 pages | ~45 seconds | instant |
| ~3000 pages | ~2 minutes | instant |

The JSON index is built once. Every `--page`, `--area`, or `--view` after that reads from cache —
no source files are re-read.

Use `--rebuild` to refresh the index after making source code changes.

---

## Sharing With Your Team

- Commit the `aspx-analysis-skill/` folder inside `.github/skills/` to your repo
- Every developer gets the skill automatically on `git pull`
- No additional setup for team members who already have Copilot + Python 3.8+
- The `_aspx_index.json` can optionally be committed too — team members skip the parse step entirely

---

## Troubleshooting

**"No ASPX files found"**
- Confirm the project is ASP.NET Web Forms (not MVC, Blazor, or Razor Pages)
- Check that `.aspx` files exist in the target path
- If files are in an unusual location, pass the specific subfolder as the target

**Copilot doesn't activate the skill**
- Confirm `SKILL.md` is at `.github/skills/aspx-analysis-skill/SKILL.md` (workspace root)
- Switch Copilot Chat to Agent Mode (not inline suggestions mode)
- Try an explicit trigger phrase: `analyze aspx pages in this repo`

**Python not found**
```bash
python --version   # if this fails:
python3 --version  # try python3
# If neither works, install Python from https://python.org
```

**Encoding error on Windows terminal**
- The script forces UTF-8 output internally
- If you see `?` for special characters in the terminal, they render correctly in the saved `.md` files
- Open `{project}_aspx_project.md` in VS Code for full fidelity

**Index is stale after code changes**
```bash
python .github/skills/aspx-analysis-skill/scripts/aspx_analysis_skill.py . --rebuild --view project
```
