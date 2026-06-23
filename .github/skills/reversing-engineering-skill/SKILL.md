---
name: reversing-engineering-skill
description: 'Reverse-engineer a legacy .NET Framework 4.8 ASP.NET Web Forms application (.aspx / .ascx / .master + C# or VB code-behind) and extract the COMPLETE business logic as structured markdown — end-to-end business workflows, rules, validations, conditions, calculations, field/data transformations, cross-layer dependencies, database interactions, external integrations, and data-flow mappings. Focus on functional/business behavior, not a line-by-line code explanation. Use when asked to analyze or reverse-engineer ASPX or Web Forms code, extract business logic or business rules from legacy .NET, document a screen''s functional behavior, trace logic across UI → business → service → repository → stored procedure, or prepare a legacy application for modernization or migration.'
---

# Legacy .NET Reverse-Engineering Analysis

**Act as a senior reverse-engineering analyst** for a legacy **.NET Framework 4.8**
ASP.NET Web Forms application. Analyze the files provided to you and **reconstruct
the complete business process** they implement. The output serves Business
Analysts, Product Owners, Architects, and Modernization/Migration teams.

You will be given one or more of:

- An `.aspx` page (and/or `.ascx` user control, `.master` layout)
- Its code-behind (`.aspx.cs` / `.aspx.vb`)
- Any referenced helper classes, business-layer classes, repositories, services,
  stored procedures, DTOs/models, or configuration (`web.config`) — when available

> **Scope:** Analyze **only the files provided in context**. Do not assume any
> build tools, scripts, or project structure. If a referenced dependency's source
> is not provided, document it as a dependency and describe its **inferred**
> purpose from how it is used.

---

## Core Instructions (follow strictly)

- Identify the **end-to-end business flow** implemented in the files.
- Extract **all** business rules, validations, conditions, calculations, and
  field/data transformations.
- When a method invokes logic in another application layer or component, **trace
  that dependency and include the downstream business logic** as well.
- **Do not** provide only a technical code explanation — focus on the
  **functional / business behavior** (what it means for the business and the user).
- Capture interactions with **services, repositories, helper classes, APIs,
  database objects, session/context objects, and configuration values**.
- If full downstream code is not available, clearly **mention the dependency** and
  describe its **inferred purpose based on usage** (mark `(inferred)` and give a
  confidence level).

---

## 1. Screen / Page Overview

For each page, state:

- **Business purpose** of the screen
- **Target users / roles**
- **Main business capability** provided
- **Inputs** captured from users
- **Outputs** generated / displayed

---

## 2. End-to-End Business Flow

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

## 3. Detailed Method Analysis (core deliverable)

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
  triggered. Trace into called services / repositories / helpers.
- **Validation Rules** — every validator (`RequiredFieldValidator`,
  `RegularExpressionValidator`, `RangeValidator`, `CompareValidator`,
  `CustomValidator`, `Page.IsValid`) stated as a business rule.
- **Conditional Rules** — guard clauses (`IsNullOrEmpty`, `TryParse`, null
  checks), `if/else/switch` branching, and thrown exceptions — as business
  conditions.
- **Calculations** — formulas, totals, rounding, tax/discount/interest logic.
- **Data Transformations** — type conversions, formatting, mapping between source
  and destination fields.
- **Called Components / Dependencies** — services, repositories, helpers, APIs,
  stored procedures, DB objects. For each, include:
  - Purpose · Inputs · Outputs · Business Impact
- **Data Flow / Mappings** — request/query/form inputs → fields/properties →
  service/DB calls → session / ViewState / config → response/redirect/UI.
  Include field-to-field and parameter-to-stored-proc mappings where visible.

### Downstream Logic Trace
When a method crosses layers, trace as far as the provided source allows:

```
UI Layer → Business Layer → Service Layer → Repository Layer → Stored Procedure
```

If the downstream source is unavailable, record:

| Dependency | Inferred Purpose | Evidence | Confidence |
|------------|------------------|----------|------------|
| `OrderService.Place()` | Persists order + charges payment | called on checkout click | Medium |

---

## 4. Data Flow Mapping

| Source Field | Destination Field | Transformation | Business Meaning |
|--------------|-------------------|----------------|------------------|

## 5. Business Rules Extracted

| Rule ID | Business Rule | Trigger Condition | Outcome |
|---------|---------------|-------------------|---------|

## 6. Database Interaction Analysis

Document: **Tables Read**, **Tables Updated**, **Stored Procedures Executed**,
**Views Accessed**, and the **Insert / Update / Delete** logic with its business
intent.

## 7. External Integration Analysis

Document: **REST APIs**, **SOAP Services**, **File Uploads**, **Email Triggers**,
**Message Queues**, and **Third-party Systems** — each with purpose and impact.

## 8. Screen Control Analysis

| Control ID | Control Type | Business Purpose | Validation | Backend Field | Methods Used |
|------------|--------------|------------------|------------|---------------|--------------|

---

## 9. Functional Summary

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
  config keys found in the provided source — never generic placeholders.
- Mark anything inferred as **`(inferred)`** with a confidence level.
- Use **business language** ("validates the customer's credit limit before
  checkout") over mechanical phrasing ("calls a method on an object").
- **Always trace business logic across layers** whenever the code is available.
- Output **markdown only**, skimmable: headings + bullets + tables, not walls of
  prose.

---

> **Start here:** analyze the `.aspx` and its code-behind currently provided in
> context. If nothing is attached, ask which file(s) to analyze.
