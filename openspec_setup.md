# OpenSpec Setup & Spec-Driven Development Guide

Complete guide for pairing this repo's [aspx-analyzer](.claude/skills/aspx-analyzer/SKILL.md)
skill with [OpenSpec](https://github.com/Fission-AI/OpenSpec) — from installing the CLI,
to reverse-engineering a legacy ASP.NET Web Forms repo into an OpenSpec-friendly project,
to running Spec-Driven Development (SDD) day-to-day for every new feature and business
capability afterward.

Two repos are involved and it's easy to mix them up:

- **This repo** (`aspx-analysis-skill`) — ships the `aspx-analyzer` Claude Code skill.
  You don't run OpenSpec *inside* this repo (unless you're extending the skill itself —
  see [Part G](#part-g--optional-using-openspec-on-this-skill-repo-itself)).
- **Your target repo** — the legacy ASP.NET Web Forms app you're modernizing. OpenSpec
  and the aspx-analyzer output both live there.

---

## Table of Contents

- [Part A — What OpenSpec Is, In One Page](#part-a--what-openspec-is-in-one-page)
- [Part B — Installing OpenSpec](#part-b--installing-openspec)
- [Part C — Initializing OpenSpec in Your Target Repo](#part-c--initializing-openspec-in-your-target-repo)
- [Part D — Reverse-Engineering a Legacy Repo Into OpenSpec (the aspx-analyzer handoff)](#part-d--reverse-engineering-a-legacy-repo-into-openspec-the-aspx-analyzer-handoff)
- [Part E — Day-to-Day SDD: Building Every Feature Through OpenSpec](#part-e--day-to-day-sdd-building-every-feature-through-openspec)
- [Part F — Full CLI Reference](#part-f--full-cli-reference)
- [Part G — Customizing config.yaml, Schemas, and Rules](#part-g--customizing-configyaml-schemas-and-rules)
- [Part H — Recommended Repo Layout](#part-h--recommended-repo-layout)
- [Part I — Troubleshooting / FAQ](#part-i--troubleshooting--faq)
- [Part J — Optional: Using OpenSpec on This Skill Repo Itself](#part-j--optional-using-openspec-on-this-skill-repo-itself)

---

## Part A — What OpenSpec Is, In One Page

OpenSpec is a **spec layer**, not a project-management tool. The core idea: agree on
*what* to build, in writing, before an AI assistant (or a human) writes a line of code.

Four artifact types, one per change:

| Artifact | Answers |
|---|---|
| **proposal.md** | Why is this change happening? What changes? What's the impact/blast radius? |
| **specs / spec deltas** | What are the exact functional requirements (Given/When/Then scenarios)? |
| **design.md** | How will it be built — architecture, data model, key decisions? |
| **tasks.md** | What's the ordered checklist of implementation steps? |

Specs are **living** — once a change is archived, its spec deltas merge into
`openspec/specs/`, which becomes the durable source of truth for what the system does.
Six months later, `openspec/specs/` tells you the actual behavior, not just what the
original PR description claimed.

For **this project's use case** (legacy ASP.NET Web Forms → modernization), OpenSpec
gives you a structured place to land what the aspx-analyzer skill discovers: each
business capability it finds (Orders, Administration, Authentication, ...) becomes one
OpenSpec change proposal, pre-populated with the actual legacy pages, auth model, and
data-access facts — not a blank page.

---

## Part B — Installing OpenSpec

Requires Node.js. Install the CLI globally:

```bash
npm install -g @fission-ai/openspec@latest
```

Also works with `pnpm`, `yarn`, `bun`, or `nix` if that's your toolchain's convention —
substitute your package manager's global-install form.

Verify:

```bash
openspec --version
```

Keep it current later with:

```bash
npm install -g @fission-ai/openspec@latest   # re-run to upgrade the CLI itself
openspec update                              # refreshes an already-initialized repo's
                                              # generated AI-tool instructions/skills
```

---

## Part C — Initializing OpenSpec in Your Target Repo

Run this **inside the legacy repo you're modernizing** (not inside `aspx-analysis-skill`):

```bash
cd /path/to/YourLegacyWebFormsApp
openspec init --tools claude
```

`--tools claude` tells OpenSpec to generate Claude Code integration (slash commands under
`.claude/skills/`). Pass `--tools all` to generate integration for every supported AI
assistant, or `--tools none` for a bare scaffold you wire up manually. `--profile core`
(default) or `--profile expanded` picks which workflow commands get installed — see
[Part E](#part-e--day-to-day-sdd-building-every-feature-through-openspec) for the
difference.

This creates:

```
YourLegacyWebFormsApp/
├── openspec/
│   ├── specs/            ← durable source of truth (empty until your first archive)
│   ├── changes/          ← in-flight change proposals live here
│   └── config.yaml       ← project context + rules (schema: spec-driven by default)
└── .claude/
    └── skills/            ← OpenSpec's own /opsx:* skills (separate from aspx-analyzer)
```

Nothing here is ASPX-specific yet — this is the generic OpenSpec scaffold. The
ASPX-specific content comes from aspx-analyzer in Part D.

If the repo already has some `openspec/` remnants from a previous partial setup, add
`--force` to auto-clean legacy files before re-scaffolding.

---

## Part D — Reverse-Engineering a Legacy Repo Into OpenSpec (the aspx-analyzer handoff)

This is where `aspx-analysis-skill`'s `aspx-analyzer` skill and OpenSpec meet. Order
matters — OpenSpec's scaffold must exist first (Part C) before the emitter fills content
into it.

### Step 1 — Get the aspx-analyzer skill into the target repo

Copy (or `git submodule` / symlink, your call) this repo's skill folder into the target:

```
YourLegacyWebFormsApp/.claude/skills/aspx-analyzer/   ← copy from this repo
```

It's the same `.claude/skills/aspx-analyzer/` directory that lives in
[this repo](.claude/skills/aspx-analyzer/) — nothing to rebuild, just drop it in. Claude
Code auto-discovers it the moment it's under `.claude/skills/`.

### Step 2 — Reverse-engineer the legacy app

In Claude Code, opened at the target repo:

```
Analyze the ASPX pages in this repo
```

or, running the script directly:

```bash
python .claude/skills/aspx-analyzer/scripts/aspx_analysis_skill.py . --view project --save-report
```

For a 10,000+ page legacy monolith, add `--workers 8` (parallel, memory-safe by default —
see the skill's own docs for details). This produces
`{repo}/{repo}_aspx_index.json` — the persistent index every later step reads from
without re-parsing source.

### Step 3 — Project the index into OpenSpec

```bash
python .claude/skills/aspx-analyzer/scripts/aspx_openspec_emitter.py \
    ./{repo}/{repo}_aspx_index.json --openspec-dir ./openspec
```

Or just ask Claude Code: *"generate openspec config"* / *"prep this repo for
modernization"* — the skill's SKILL.md has this as Step 8 of its playbook and runs the
same command for you.

This writes:

- **`openspec/config.yaml`** — inside a marked auto-generated block:
  - `context:` — stack (.NET Framework Web Forms), auth mode, page/control/master
    counts, direct-SQL debt count, the full capability list with page counts.
  - `rules.proposal` — e.g. "every proposal must name which legacy pages it replaces",
    "preserve discovered auth roles", "capabilities with direct SQL need a data-access
    migration plan, not a lift-and-shift".
  - `rules.specs` — e.g. "reference actual legacy page names, don't invent screens",
    "flag any page with auth: unknown as a spec risk".
  - Re-running the emitter after you `--rebuild` the aspx index only refreshes this
    block — anything you've hand-added to `config.yaml` outside the markers survives.

- **`openspec/changes/<area-slug>/proposal.md`** — one per functional area/capability
  (Authentication, Orders, Administration, ...), pre-filled with:
  - `## Why` — the actual legacy page list, each with purpose + auth requirement, and a
    called-out data-access risk section if any page uses direct SQL.
  - `## What Changes` — left as a `<!-- TODO -->` for you (or the next SDD step) to fill in.
  - `## Impact` — affected page count, unknown-auth count, direct-SQL count.
  - **Never overwrites an existing proposal.md** — safe to re-run after adding more pages
    to the legacy app; only missing stubs get created.

### Step 4 — Turn each stub into a real proposal

The stub gives you *facts*, not a *plan*. For each `openspec/changes/<area>/proposal.md`,
open it in Claude Code and continue the SDD workflow from Part E — typically:

```
/opsx:continue    (or /opsx:ff to generate specs/design/tasks in one shot)
```

pointed at that change, so the AI fills in `## What Changes` / `## Impact` and generates
the accompanying `design.md` + `tasks.md`, informed by the real legacy facts already in
`## Why` — not a generic greenfield template.

---

## Part E — Day-to-Day SDD: Building Every Feature Through OpenSpec

Once Part C/D are done, this is how you build **every subsequent feature or business
capability** — modernization work or brand-new functionality — through OpenSpec instead
of ad hoc prompting. All commands below are slash commands Claude Code exposes once
`openspec init --tools claude` has run in the target repo.

### Profiles: core vs expanded

```bash
openspec config profile          # interactive picker
openspec config profile core     # streamlined (default)
openspec config profile expanded # granular, step-by-step artifact control
```

| Profile | Commands available |
|---|---|
| **core** (default) | `/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:sync`, `/opsx:archive` |
| **expanded** | adds `/opsx:new`, `/opsx:continue`, `/opsx:ff`, `/opsx:verify`, `/opsx:bulk-archive`, `/opsx:onboard` |

Start on `core`. Switch to `expanded` once you want fine-grained control over generating
proposal/specs/design/tasks as separate steps instead of one bundled `/opsx:propose`.

### The loop, every time you build something

```
1. /opsx:explore "<rough idea or problem statement>"
   — optional thinking phase, no commitment yet. Use this when you're not sure the
     feature is well-scoped, e.g. before touching a modernization capability with
     messy legacy behavior.

2. /opsx:propose "<feature description>"
   — creates openspec/changes/<change-name>/ with proposal.md + specs + design.md +
     tasks.md generated together (core profile's quick path).
   — expanded profile: /opsx:new "<name>" then /opsx:continue (repeat per artifact)
     or /opsx:ff to fast-forward through all of them at once.

3. Review the generated proposal.md / specs / design.md / tasks.md yourself (or with
   a teammate) BEFORE implementation starts. This is the actual point of SDD — catch
   a wrong assumption on paper, not three files into a refactor.

4. /opsx:apply
   — implements tasks.md's checklist, updating the change's artifacts as it goes if
     reality diverges from the plan.

5. /opsx:verify        (expanded profile only)
   — validates the implementation against the specs/design it was built from.

6. /opsx:sync          (optional, either profile)
   — syncs the change's delta specs into openspec/specs/ before archiving, if you
     want the durable spec updated ahead of archive.

7. /opsx:archive
   — marks the change complete, merges its spec deltas into openspec/specs/ (durable
     source of truth), moves the change folder to history.
```

Repeat step 1-7 for **every feature** — a new Orders capability rewrite, a bugfix with
behavior implications, an auth model change, anything. The migration proposals seeded by
aspx-analyzer in Part D are just the first batch of changes fed into this exact same loop.

### Checking status mid-flight

```bash
openspec list                 # all in-flight changes
openspec list --specs         # durable specs instead
openspec show <change-name>   # view one change's artifacts
openspec status --change <id> # where a change stands in its schema's artifact sequence
openspec validate <name> --strict   # catch structural problems before /opsx:apply
```

---

## Part F — Full CLI Reference

Beyond the OPSX slash commands (Claude Code-facing), the underlying `openspec` CLI has
its own commands you'll use directly from a terminal:

### Setup
```
openspec init [path] [--tools <list>] [--force] [--profile <core|expanded>]
openspec update [path] [--force]              # refresh generated AI-tool instructions
```

### Browsing
```
openspec list [--specs|--changes] [--sort recent|name] [--json]
openspec view                                 # interactive browser
openspec show <item-name> [--type change|spec] [--requirements] [--no-scenarios]
```

### Validation
```
openspec validate <name> [--all] [--changes] [--specs] [--strict] [--json]
```

### Lifecycle
```
openspec new change <name> [--description <text>] [--goal <text>] [--schema <name>]
openspec archive <change-name> [-y] [--skip-specs] [--no-validate]
openspec status [--change <id>] [--schema <name>]
```

### Schemas (custom workflow templates)
```
openspec schemas [--json]                     # list schemas available in this project
openspec schema init <name> [--artifacts <list>] [--default]
openspec schema fork <source> [name]          # copy + customize an existing schema
openspec schema validate [name] [--verbose]
openspec schema which [name] [--all]
openspec templates [--schema <name>]          # inspect a schema's artifact templates
openspec instructions [artifact] --change <id> # the exact instructions an artifact step gets
```

### Configuration
```
openspec config path                          # where config.yaml lives
openspec config list                          # dump current settings
openspec config get <key>
openspec config set <key> <value>
openspec config unset <key>
openspec config edit                          # open in $EDITOR
openspec config profile [core|expanded]
```

### Health
```
openspec doctor [--json]                      # sanity-check the openspec/ setup
openspec context [--json]                     # what context gets injected into prompts
```

### Multi-repo (advanced — skip unless you're centralizing specs across repos)
```
openspec store setup|register|unregister|remove|list|doctor
openspec workset create|list|open|remove
```

Global flags on every command: `--version`, `--no-color`, `--help`.

---

## Part G — Customizing config.yaml, Schemas, and Rules

### config.yaml

```yaml
schema: spec-driven          # default schema for new changes
context: |                   # injected into every artifact-generation prompt
  Tech stack: ASP.NET Web Forms (.NET Framework) migrating to <your target stack>.
  ...
rules:
  proposal:
    - "Include a rollback plan for any change touching Authentication."
  specs:
    - "Use Given/When/Then format."
```

- `context` applies to **every** artifact type generated.
- `rules.<artifact>` only applies when generating that specific artifact.
- The aspx-analyzer emitter (Part D) writes into a marked block inside this same file —
  hand-added keys outside that block are never touched by re-running the emitter. If you
  add your own top-level `context:`/`rules:` keys *outside* the marker block, the emitter
  detects the conflict and appends its block separately with a warning rather than
  silently overwriting — merge them by hand at that point.

### Schemas (only if the default proposal/specs/design/tasks shape doesn't fit)

```bash
openspec schema fork spec-driven my-modernization-workflow
openspec config set schema my-modernization-workflow   # make it the project default
```

Forked schemas live in `openspec/schemas/<name>/` with their own `schema.yaml` +
`templates/{proposal,spec,design,tasks}.md` — edit the templates directly to change what
questions each artifact asks. Useful if, say, every modernization proposal in your repo
should always have a "Legacy Pages Replaced" table (which aspx-analyzer already fills in
via `## Why`, so you may not need to).

---

## Part H — Recommended Repo Layout

For a legacy repo being modernized with both tools in play:

```
YourLegacyWebFormsApp/
├── openspec/
│   ├── specs/                        durable source of truth (grows via /opsx:archive)
│   ├── changes/
│   │   ├── authentication/proposal.md    ← seeded by aspx-analyzer, fleshed out via SDD
│   │   ├── orders/proposal.md
│   │   ├── administration/proposal.md
│   │   └── add-payment-webhook/          ← a brand-new feature, same SDD loop, no
│   │       proposal.md                     legacy facts needed for this one
│   └── config.yaml                   context + rules (aspx-analyzer's block + yours)
├── .claude/
│   └── skills/
│       ├── aspx-analyzer/            ← copied in from this repo
│       └── (opsx skills)             ← generated by `openspec init --tools claude`
├── {repo}_aspx_index.json            aspx-analyzer's cached parse (commit or .gitignore, your call)
└── ... your actual legacy app source ...
```

Commit `openspec/` and `.claude/skills/` to source control — the whole point of SDD is
that specs and proposals are durable, reviewable artifacts, not throwaway chat output.

---

## Part I — Troubleshooting / FAQ

**"Do I run `openspec init` in `aspx-analysis-skill` or in my legacy app?"**
Your legacy app. This repo only *provides* the aspx-analyzer skill; it doesn't consume
OpenSpec itself unless you opt into [Part J](#part-j--optional-using-openspec-on-this-skill-repo-itself).

**`aspx_openspec_emitter.py` errors "openspec dir does not exist"**
Run `openspec init --tools claude` in the target repo first (Part C). The emitter only
fills content into an existing `openspec/` scaffold — it deliberately never creates one,
so it can't be run against a repo that hasn't opted into OpenSpec yet.

**Re-ran the emitter after adding new legacy pages — did it clobber my edited proposals?**
No. Proposal stubs are created only if missing; `config.yaml` is only touched inside its
marked auto-generated block. Anything you wrote in `## What Changes`/`## Impact`, or
added to `config.yaml` outside the markers, is preserved.

**Which slash commands exist depends on my profile — how do I check?**
`openspec config profile` shows/sets it. `core` = propose/apply/sync/archive/explore.
`expanded` adds new/continue/ff/verify/bulk-archive/onboard.

**I want OpenSpec's spec-driven flow for brand-new features that have nothing to do with
the legacy migration.**
Same loop, Part E, starting from `/opsx:propose` directly — you don't need aspx-analyzer
at all for greenfield work. aspx-analyzer only matters for seeding proposals from
*existing* legacy code.

---

## Part J — Optional: Using OpenSpec on This Skill Repo Itself

If you want to develop **`aspx-analysis-skill` itself** (this repo) with SDD — e.g.
adding a new report view or extending the engine — nothing above changes conceptually,
you just run `openspec init --tools claude` here instead of in a target legacy app, and
skip Part D entirely (there's no legacy ASPX code in this repo to reverse-engineer; you'd
go straight to Part E's `/opsx:propose` loop for each new capability you add to the skill).
