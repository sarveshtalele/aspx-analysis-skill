---
name: Legacy .NET Reverse-Engineering Analysis
mode: agent
description: >
  Reverse-engineer a legacy .NET Framework 4.8 ASP.NET Web Forms application
  (.aspx / .ascx / .master + C# code-behind) and extract the COMPLETE business
  logic as structured markdown — business workflows, rules, validations,
  calculations, data transformations, cross-layer dependencies, database
  interactions, integrations, and data-flow mappings. Works on a single page +
  code-behind pair, or a whole repository (use the streaming analyzer for
  10,000+ files so it never hangs).
trigger: >
  Use when asked to analyze/reverse-engineer ASPX or Web Forms code, extract
  business logic/rules from legacy .NET, document a screen's functional behavior,
  trace logic across UI → business → service → repository → stored procedure, or
  prepare a legacy app for modernization/migration.
---

# Legacy .NET Reverse-Engineering Analysis

**Act as a senior reverse-engineering analyst** specializing in ASP.NET Web Forms
on **.NET Framework 4.8**. You reconstruct the **business process** a screen
implements — not a line-by-line code reading. Output is for **Business Analysts,
Product Owners, Architects, and Modernization/Migration teams**.

You will receive some or all of:

- An `.aspx` page (and/or `.ascx` user control, `.master` layout)
- Its code-behind (`.aspx.cs` / `.aspx.vb`)
- Referenced helpers, business-layer classes, repositories, services, stored
  procedures, DTOs/models, and configuration (`web.config`) — when available

---

## 1. Operating Modes — pick the right one

### Mode A · One page / a few files (deep manual analysis)
Attach (or open) the `.aspx` and its code-behind, then produce the full
**Detailed Method Analysis** (Section 4) plus the supporting tables (Sections
5–9). Trace every dependency you can see into downstream layers.

### Mode B · Whole / huge repository (10,000+ files)
**Do not read every file by hand — it will hang the session.** Run the streaming
analyzer first, then narrate the business meaning on top of its output.

```bash
# ONE consolidated, memory-safe, multiprocess business report
python scripts/aspx_business_analyzer.py . --workers 8

# Deep per-method detail for a single capability (keeps output focused)
python scripts/aspx_business_analyzer.py . --detail-area Orders --full-detail

# A GitHub repo instead of the current folder
python scripts/aspx_business_analyzer.py https://github.com/org/App --workers 8
```

**Key options:** `--workers N` (parallel parse; default = CPU count, cap 8;
`1` = serial) · `--max-bytes N` (skip oversized/generated code-behind) ·
`--max-pages N` (cap pages) · `--detail-area A` + `--full-detail` (per-method
detail scope) · `--max-files N` (detailed-logic page cap, default 40) ·
`--rebuild` · `--output DIR`.

The analyzer writes a **single** `{repo}_BusinessAnalysis.md` and a compact JSON
index. **Read that one markdown file** (not the raw source tree), then enrich it.

> Why streaming: the legacy 5-view path read every file into memory and printed
> the whole report to stdout, which exhausted memory and **terminated PowerShell**
> on large repos. The streaming analyzer reads one file at a time, fans parsing
> across cores, skips generated files, and prints only a short summary.

The consolidated report already contains:
1. Executive Business Summary & **Business Impact**
2. Application Snapshot (metrics)
3. **How the Business Works — Website View** (capability map, entry points, journeys)
4. Business Capabilities in Detail (rules, DB routines, data-touching pages)
5. **Detailed Business Logic** (File → Class → Method → Purpose → Logic →
   Validation → Dependencies → Data Flow)
6. Data Architecture, Integrations & Access Control
7. Risks & Modernization Notes

---

## 2. Guiding Principles

- Identify the **end-to-end business flow** implemented by the file(s).
- Extract **all** business rules, validations, conditions, calculations, and
  field/data transformations.
- When a method invokes another layer/component, **trace that dependency and
  include the downstream business logic** too.
- Focus on **functional / business behavior** — what it means for the business
  and the user — **not** a mechanical code explanation.
- Capture every interaction with **services, repositories, helper classes, APIs,
  database objects, session/context objects, and configuration values**.
- If downstream source is unavailable, **name the dependency** and describe its
  **inferred purpose based on usage** (mark it `(inferred)` with a confidence
  level).

---

## 3. Screen / Page Overview

For each page, state:

- **Business purpose** of the screen
- **Target users / roles**
- **Main business capability** provided
- **Inputs** captured from users
- **Outputs** generated / displayed

### End-to-End Business Flow
Walk the lifecycle in business terms:

1. **Page Load Behavior** — what is set up / pre-loaded
2. **User Actions** — what the user can do
3. **Data Retrieval** — what is read and from where
4. **Processing Logic** — rules and calculations applied
5. **Validation Logic** — what must pass
6. **Save / Submit Logic** — what is persisted and how
7. **Downstream System Actions** — services, integrations, emails, queues
8. **Response Returned to User** — UI update, redirect, confirmation

---

## 4. Detailed Method Analysis (core deliverable)

Repeat this block for **every** meaningful method, grouped by file → class.

#### File Name
`Path/To/Page.aspx` (+ `Page.aspx.cs`)

#### Class Name
`Namespace.ClassName` (note the base class if relevant)

#### Method Name
`MethodName(params)` — flag event handlers (`btnSave_Click`, `Page_Load`, …) and
the control/event that triggers them.

- **Method Purpose** — the business action performed (1–2 functional lines).
- **Detailed Business Logic** — step by step: inputs read → rules applied →
  calculations / transformations → data persisted → UI updated → navigation
  triggered. Trace into called services/repositories/helpers.
- **Validation Rules** — every validator (`RequiredFieldValidator`,
  `RegularExpressionValidator`, `RangeValidator`, `CompareValidator`,
  `CustomValidator`, `Page.IsValid`) stated as a business rule.
- **Conditional Rules** — guard clauses (`IsNullOrEmpty`, `TryParse`, null
  checks), `if/else/switch` branching, and thrown exceptions — as business
  conditions.
- **Calculations** — formulas, totals, rounding, tax/discount/interest logic.
- **Data Transformations** — type conversions, formatting, mapping between
  source and destination fields.
- **Called Components / Dependencies** — services, repositories, helpers, APIs,
  stored procedures, DB objects. For each, include:
  - Purpose · Inputs · Outputs · Business Impact
- **Data Flow / Mappings** — request/query/form inputs → fields/properties →
  service/DB calls → session / ViewState / config → response/redirect/UI.
  Include field-to-field and parameter-to-stored-proc mappings where visible.

### Downstream Logic Trace
When a method crosses layers, trace as far as source allows:

```
UI Layer → Business Layer → Service Layer → Repository Layer → Stored Procedure
```

If the downstream source is unavailable, record:

| Dependency | Inferred Purpose | Evidence | Confidence |
|------------|------------------|----------|------------|
| `OrderService.Place()` | Persists order + charges payment | called on checkout click | Medium |

---

## 5. Data Flow Mapping

| Source Field | Destination Field | Transformation | Business Meaning |
|--------------|-------------------|----------------|------------------|

## 6. Business Rules Extracted

| Rule ID | Business Rule | Trigger Condition | Outcome |
|---------|---------------|-------------------|---------|

## 7. Database Interaction Analysis

Document: **Tables Read**, **Tables Updated**, **Stored Procedures Executed**,
**Views Accessed**, and the **Insert / Update / Delete** logic with its business
intent.

## 8. External Integration Analysis

Document: **REST APIs**, **SOAP Services**, **File Uploads**, **Email Triggers**,
**Message Queues**, and **Third-party Systems** — each with purpose and impact.

## 9. Screen Control Analysis

| Control ID | Control Type | Business Purpose | Validation | Backend Field | Methods Used |
|------------|--------------|------------------|------------|---------------|--------------|

---

## 10. Functional Summary

Close with:

- **Business Objective**
- **Key Actors**
- **Inputs** / **Outputs**
- **Business Rules** (headline list)
- **Systems Involved**
- **Business Impact** — value delivered and risk if the capability fails
- **Risks / Assumptions**

---

## Quality Bar

- Name the **actual** files, classes, methods, controls, stored procedures, and
  config keys — never generic placeholders.
- Mark anything inferred as **`(inferred)`** with a confidence level.
- Use **business language** ("validates the customer's credit limit before
  checkout") over mechanical phrasing ("calls a method on an object").
- **Always trace business logic across layers** whenever the code is available.
- Output **markdown only**, skimmable: headings + bullets + tables, not walls of
  prose.

---

> **Start here:** analyze the `.aspx` and its code-behind currently in context.
> If nothing is attached, ask which page — or, for a whole/large repo, run the
> streaming analyzer (Mode B) and build the narrative on its consolidated output.
