# Legacy .NET Reverse-Engineering Analysis — Skill

A **self-contained** AI skill that turns legacy **.NET Framework 4.8 / ASP.NET
Web Forms** code into a structured **business-logic** specification in markdown.

It reads the `.aspx` / `.ascx` / `.master` and its `.aspx.cs` / `.aspx.vb`
code-behind you provide and reconstructs the **end-to-end business process** —
not a line-by-line code walkthrough.

> **Independent:** this skill depends only on its own instructions and the files
> you give it. No scripts, build tools, libraries, or project layout required.
> Drop the folder into any project (or use it on its own).

---

## What it produces

A single markdown report covering:

1. **Screen / Page Overview** — purpose, users/roles, capability, inputs, outputs
2. **End-to-End Business Flow** — load → user actions → retrieval → processing →
   validation → save → downstream actions → response
3. **Detailed Method Analysis** — for every method, in this order:
   - File Name · Class Name · Method Name
   - Method Purpose
   - Detailed Business Logic
   - Validation Rules · Conditional Rules · Calculations · Data Transformations
   - Called Components / Dependencies (purpose · inputs · outputs · impact)
   - Data Flow / Mappings
   - Downstream Logic Trace (UI → Business → Service → Repository → Stored Proc)
4. **Data Flow Mapping** table
5. **Business Rules Extracted** table
6. **Database Interaction Analysis** (tables, stored procs, views, CRUD intent)
7. **External Integration Analysis** (REST/SOAP/email/queues/3rd-party)
8. **Screen Control Analysis** table
9. **Functional Summary** — objective, actors, I/O, rules, systems, business
   impact, risks/assumptions

Dependencies whose source is not provided are listed with an **inferred** purpose
and a confidence level.

---

## Files

This is a **GitHub Copilot Agent Skill** (not a prompt file). It lives at
`.github/skills/reversing-engineering-skill/`.

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill itself — frontmatter (`name`, `description`) + persona, instructions, and required output format. |
| `README.md` | This guide. |

---

## How to use

### GitHub Copilot (Agent Skill)
1. Keep this folder at `.github/skills/reversing-engineering-skill/` in your repo
   (project-wide), or at `~/.github/skills/reversing-engineering-skill/` (personal,
   all repos). Copilot auto-discovers skills by the `SKILL.md` frontmatter
   `description`.
2. Open the `.aspx` and its code-behind.
3. Ask Copilot to analyze them — it matches the skill on intent (e.g. "extract the
   business logic from this Web Forms page"). The `name` must equal the folder
   name (`reversing-engineering-skill`).

### Claude / Claude Code
Reference or paste `SKILL.md`, then attach the page + code-behind (and any
helper/service/repository/stored-proc files you have). Ask it to produce the
analysis.

### Any other AI assistant
`SKILL.md` is plain markdown — use its body as the system/instruction prompt and
supply the source files as input.

---

## Input checklist (the more you provide, the deeper the trace)

- [x] `.aspx` / `.ascx` / `.master` markup
- [x] Code-behind (`.aspx.cs` / `.aspx.vb`)
- [ ] Business-layer / service / repository classes
- [ ] Helper / utility classes, DTOs, models
- [ ] Stored procedures / SQL
- [ ] `web.config` (connection strings, app settings)

Missing items are still handled — they're reported as dependencies with inferred
purpose and confidence.

---

## Output quality bar

- Names the **actual** files, classes, methods, controls, stored procs, and
  config keys — no generic placeholders.
- Anything not directly observed is marked **`(inferred)`** with confidence.
- **Business language** over mechanical phrasing.
- **Markdown only** — headings, bullets, tables; skimmable.
