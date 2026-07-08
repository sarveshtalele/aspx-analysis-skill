# OpenSpec Setup & Spec-Driven Development Guide

Complete guide for pairing this repo's [aspx-analyzer](.claude/skills/aspx-analyzer/SKILL.md)
skill with [OpenSpec](https://github.com/Fission-AI/OpenSpec) — from installing the CLI,
to reverse-engineering a legacy ASP.NET Web Forms repo into an OpenSpec-friendly project,
to running Spec-Driven Development (SDD) day-to-day for every new feature and business
capability afterward.

**Want to see this actually run against a real repo first?** See
[EXAMPLE_WALKTHROUGH.md](EXAMPLE_WALKTHROUGH.md) — every command below, run for real
against [syncfusion/aspnet-ej1-demos](https://github.com/syncfusion/aspnet-ej1-demos)
(1147 pages), including a full legacy-to-modern migration of one real capability and a
multi-user collaboration workflow this document doesn't cover.

Two repos are involved and it's easy to mix them up:

- **This repo** (`aspx-analysis-skill`) — ships the `aspx-analyzer` Claude Code skill.
  You don't run OpenSpec *inside* this repo (unless you're extending the skill itself —
  see [Part J](#part-j--optional-using-openspec-on-this-skill-repo-itself)).
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

Verified output (CLI v1.5.0):

```
- Creating OpenSpec structure...
▌ OpenSpec structure created
- Setting up Claude Code...
✔ Setup complete for Claude Code

OpenSpec Setup Complete

Created: Claude Code
5 skills and 5 commands in .claude/
Config: openspec/config.yaml (schema: spec-driven)

Getting started:
  Start your first change: /opsx:propose "your idea"
```

(That `/opsx:propose` suggestion in the CLI's own output doesn't match the actual skill
folder names it just created — `openspec-propose`, not `opsx:propose`. Harmless CLI
wording quirk in v1.5.0; invoke the real skill by its real name, `openspec-propose`.)

`--tools claude` tells OpenSpec to generate Claude Code integration. Pass `--tools all`
for every supported AI assistant, or `--tools none` for a bare scaffold you wire up
manually. **Only `openspec/config.yaml` is created immediately** — `openspec/specs/` and
`openspec/changes/` don't exist as folders yet; they're created on demand the first time
you run `openspec new change` (Part D/E), so don't be surprised if you don't see them
right after `init`.

This creates:

```
YourLegacyWebFormsApp/
├── openspec/
│   └── config.yaml       ← project context + rules (schema: spec-driven)
└── .claude/
    └── skills/
        ├── openspec-propose/         ← create a change + all 4 artifacts in one step
        ├── openspec-explore/         ← think through an idea before committing to a change
        ├── openspec-apply-change/    ← implement a change's tasks.md
        ├── openspec-sync-specs/      ← merge a change's delta specs into openspec/specs/
        └── openspec-archive-change/  ← mark a change complete, move it to changes/archive/
```

Each is a real Claude Code Agent Skill under `.claude/skills/<name>/SKILL.md` — same
discovery mechanism as `aspx-analyzer` itself, just a different provider (OpenSpec, not
this repo). Nothing here is ASPX-specific yet — that comes from aspx-analyzer in Part D.

If the repo already has some `openspec/` remnants from a previous partial setup, add
`--force` to auto-clean legacy files before re-scaffolding.

**Correction vs. earlier drafts of this guide:** there is no `--profile expanded` / "core
vs expanded" split with extra commands (`/opsx:new`, `/opsx:continue`, `/opsx:ff`,
`/opsx:verify`, `/opsx:bulk-archive`, `/opsx:onboard`) in the actually-installed CLI
(v1.5.0) — running `openspec config profile expanded` on the profile that does exist,
`core`, fails with `Unknown profile preset "expanded". Available presets: core`. Take the
per-artifact CLI workflow in [Part E](#part-e--day-to-day-sdd-building-every-feature-through-openspec)
(`openspec instructions <artifact> --change <name>`) as the verified granular mechanism
instead — it's real, and it's what this guide's worked example actually used.

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

The stub gives you *facts*, not a *plan*. But the emitter's stub isn't a full OpenSpec
`proposal.md` under CLI management yet — it's a plain markdown file the emitter wrote
directly. To bring it under the same instructions/status/validate machinery as any other
change, either:

- Move its content into a change created the normal way (`openspec new change <name>`,
  Part E below) and paste the stub's facts into the generated `proposal.md`, or
- Treat the stub as your own drafting scratchpad and author the real change once you're
  ready to commit to it, using the stub's `## Why` facts as your starting material.

Either way, once a real change exists, get the remaining artifacts (design, specs, tasks)
the same way this guide's worked example did — see
[Part E](#part-e--day-to-day-sdd-building-every-feature-through-openspec).

---

## Part E — Day-to-Day SDD: Building Every Feature Through OpenSpec

Once Part C/D are done, this is how you build **every subsequent feature or business
capability** — modernization work or brand-new functionality — through OpenSpec instead
of ad hoc prompting. Verified end-to-end against CLI v1.5.0 (see
[EXAMPLE_WALKTHROUGH.md](EXAMPLE_WALKTHROUGH.md) for the full real transcript against
[syncfusion/aspnet-ej1-demos](https://github.com/syncfusion/aspnet-ej1-demos)).

Only the `core` profile exists in this CLI version — `openspec config profile expanded`
errors with `Unknown profile preset "expanded". Available presets: core`. `core` gives you
5 skills: `openspec-propose`, `openspec-explore`, `openspec-apply-change`,
`openspec-sync-specs`, `openspec-archive-change`. There's a real granular, step-by-step
mechanism too — it's just CLI-driven (`openspec instructions <artifact> --change <id>`),
not a separate profile.

### The loop, every time you build something

**Fast path — one shot** (small/well-understood change): ask Claude Code to use the
`openspec-propose` skill with a description of what you want; it creates the change
directory and all 4 artifacts (proposal/design/specs/tasks) together, then:

```bash
openspec validate <change-name> --strict     # catch structural problems
```

review the 4 files yourself (or with a teammate) before implementation — the actual point
of SDD is catching a wrong assumption on paper, not three files into a refactor — then have
Claude Code use `openspec-apply-change` to implement `tasks.md`'s checklist.

**Granular path — step by step** (what this guide's worked example actually used, and
what you need whenever a change is seeded from something other than the propose skill —
e.g. an aspx-analyzer proposal stub, or you just want to review each artifact before the
next is generated):

```bash
openspec new change <name> --description "..." --goal "..."   # 1. create the shell
openspec instructions proposal --change <name>                # 2. get the proposal template
#    → author openspec/changes/<name>/proposal.md
openspec instructions design --change <name>                  # 3. get the design template
#    → author openspec/changes/<name>/design.md
openspec instructions specs --change <name>                   # 4. get the specs template
#    → author openspec/changes/<name>/specs/<capability>/spec.md
openspec instructions tasks --change <name>                   # 5. get the tasks template
#    → author openspec/changes/<name>/tasks.md
openspec status --change <name>                               # confirm 4/4 artifacts complete
openspec validate <name> --strict                             # confirm structurally valid
```

`openspec instructions <artifact>` prints the exact write path, the section-by-section
authoring rules, a fill-in-the-blanks template, and (for design/specs/tasks) which earlier
artifacts to read first — this is what an AI assistant (or you, by hand) actually follows
to write each file. Each artifact is gated on the previous one (`openspec status` shows
`[-] design (blocked by: proposal)` until the proposal exists).

**Then, either path:**

```bash
# implement tasks.md's checklist (by hand, or ask Claude Code to use openspec-apply-change)
openspec validate <name> --strict          # re-validate after implementation
openspec archive <name>                    # merge spec deltas into openspec/specs/, done
```

**Don't archive a change whose verification tasks aren't actually done.** In this guide's
worked example, the frontend build was genuinely verified (`npm run build` ran and
passed) but the backend needed a local .NET SDK not available in the authoring sandbox —
so that change was deliberately left unarchived with its remaining tasks unchecked, rather
than archived on the strength of "the files exist." Archiving is a claim that the work is
actually done and its spec deltas are trustworthy going into `openspec/specs/` — treat it
that way.

Repeat this loop for **every feature** — a capability modernization, a bugfix with
behavior implications, brand-new functionality, anything. The proposal stubs seeded by
aspx-analyzer in Part D are just a starting point fed into this same loop.

### Checking status mid-flight

```bash
openspec list                       # all in-flight changes
openspec list --specs               # durable specs instead
openspec show <change-name>         # view one change's artifacts
openspec status --change <id>       # which artifacts are done / blocked
openspec validate <name> --strict   # catch structural problems before archiving
```

---

## Part F — Full CLI Reference

Verified against the real, installed CLI (`openspec --version` → `1.5.0`):

```
$ openspec --help
Usage: openspec [options] [command]

AI-native system for spec-driven development

Commands:
  init [options] [path]              Initialize OpenSpec in your project
  update [options] [path]            Update OpenSpec instruction files
  list [options]                     List items (changes by default). Use --specs to list specs.
  view                                Display an interactive dashboard of specs and changes
  change                              Manage OpenSpec change proposals
  archive [options] [change-name]    Archive a completed change and update main specs
  spec                                Manage and view OpenSpec specifications
  config [options]                    View and modify global OpenSpec configuration
  schema                              Manage workflow schemas [experimental]
  store                                Create and manage stores - standalone OpenSpec repos
  doctor [options]                    Report relationship health for the resolved OpenSpec root
  context [options]                   Print the working context for the resolved OpenSpec root
  workset [options]                   Compose, keep, and open personal working views (local)
  validate [options] [item-name]      Validate changes and specs
  show [options] [item-name]          Show a change or spec
  feedback [options] <message>        Submit feedback about OpenSpec
  completion                          Manage shell completions
  status [options]                    Display artifact completion status for a change
  instructions [options] [artifact]   Output enriched instructions for creating an artifact
  templates [options]                 Show resolved template paths for all artifacts
  schemas [options]                   List available workflow schemas with descriptions
  new                                  Create new items
```

### Setup
```
openspec init [path] [--tools <list>] [--force]
openspec update [path] [--force]              # refresh generated AI-tool instructions
```

### Browsing
```
openspec list [--specs|--changes] [--sort recent|name] [--json]
openspec view                                 # interactive dashboard
openspec show <item-name> [--type change|spec] [--requirements] [--no-scenarios]
```

### Validation
```
openspec validate <name> [--all] [--changes] [--specs] [--strict] [--json]
```

### Lifecycle
```
openspec new change <name> [--description <text>] [--goal <text>] [--schema <name>]
openspec status [--change <id>] [--schema <name>]
openspec instructions [artifact] --change <id>   # exact write-path + template for that artifact
openspec archive [change-name] [-y] [--skip-specs] [--no-validate]
```

### Schemas (custom workflow templates — experimental)
```
openspec schemas [--json]                     # list schemas available in this project
openspec schema init <name> [--artifacts <list>] [--default]
openspec schema fork <source> [name]          # copy + customize an existing schema
openspec schema validate [name] [--verbose]
openspec schema which [name] [--all]
openspec templates [--schema <name>]          # inspect a schema's artifact templates
```

Verified: a fresh install has exactly one schema, `spec-driven` (proposal → specs →
design → tasks) — `openspec schemas` confirms nothing else ships by default.

### Configuration
```
openspec config path                          # where config.yaml lives
openspec config list                          # dump current settings
openspec config get <key>
openspec config set <key> <value>
openspec config unset <key>
openspec config edit                          # open in $EDITOR
openspec config profile [preset]              # only "core" preset exists in v1.5.0
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
│   ├── specs/                        durable source of truth (grows via `openspec archive`)
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

**What profile am I on and what does it give me?**
`openspec config profile` shows it (`openspec config list` shows the resolved workflow set
too). v1.5.0 only ships `core`: `openspec-propose`, `openspec-explore`,
`openspec-apply-change`, `openspec-sync-specs`, `openspec-archive-change`.

**I want OpenSpec's spec-driven flow for brand-new features that have nothing to do with
the legacy migration.**
Same loop, Part E, starting from `openspec new change <name>` (or the `openspec-propose`
skill) directly — you don't need aspx-analyzer at all for greenfield work. aspx-analyzer
only matters for seeding proposals from *existing* legacy code.

---

## Part J — Optional: Using OpenSpec on This Skill Repo Itself

If you want to develop **`aspx-analysis-skill` itself** (this repo) with SDD — e.g.
adding a new report view or extending the engine — nothing above changes conceptually,
you just run `openspec init --tools claude` here instead of in a target legacy app, and
skip Part D entirely (there's no legacy ASPX code in this repo to reverse-engineer; you'd
go straight to Part E's loop, `openspec new change <name>`, for each new capability you
add to the skill).
