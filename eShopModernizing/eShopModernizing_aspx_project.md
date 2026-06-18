# eShopModernizing — ASP.NET Web Forms Application Analysis

> Generated: 2026-06-18T10:19:50.674063Z

---

## Executive Summary

This is an **ASP.NET Web Forms** application with **12 pages**, **2 user controls**, and **4 master pages** across **3 functional areas**.


---

## Codebase Metrics

| Metric | Count |
|--------|-------|
| ASPX Pages | 12 |
| User Controls (.ascx) | 2 |
| Master Pages | 4 |
| Functional Areas | 3 |
| Pages with Code-Behind | 12 |
| Pages using Master Page | 12 |
| Pages with AJAX (UpdatePanel) | 0 |
| Pages with Direct SQL | 0 |
| Pages with Validators | 4 |
| Named Routes (RouteConfig) | 5 |

---

## Access Control Breakdown

| Requirement | Pages |
|-------------|-------|
| `unknown` | 5 |
| `anonymous` | 4 |
| `authenticated` | 3 |

---

## Master Pages

### `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Site.Master`
- **Purpose:** Layout master template
- **Used by:** 7 pages
- **Content Placeholders:** `MainContent`
- **ScriptManager (AJAX):** Yes

### `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Site.Master`
- **Purpose:** Layout master template
- **Used by:** 5 pages
- **Content Placeholders:** `MainContent`
- **Login Controls:** Yes
- **ScriptManager (AJAX):** Yes

### `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Site.Mobile.Master`
- **Purpose:** Mobile layout template
- **Used by:** 0 pages
- **Content Placeholders:** `HeadContent`, `FeaturedContent`, `MainContent`

### `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Site.Mobile.Master`
- **Purpose:** Mobile layout template
- **Used by:** 0 pages
- **Content Placeholders:** `HeadContent`, `FeaturedContent`, `MainContent`

---

## Functional Areas Overview

### Contact (2 pages)
- **About** — About page  *(auth: `anonymous`)*
- **Contact** — Contact page  *(auth: `anonymous`)*

### Home (2 pages)
- **Default** — Application home page / dashboard  *(auth: `anonymous`)*
- **Default** — Application home page / dashboard  *(auth: `anonymous`)*

### Products (8 pages)
- **Create** — Create new Catalog  *(auth: `unknown`)*
- **Create** — Create new Catalog  *(auth: `authenticated`)*
- **Delete** — Delete / remove confirmation — Catalog  *(auth: `unknown`)*
- **Delete** — Delete / remove confirmation — Catalog  *(auth: `authenticated`)*
- **Details** — Detail / read-only view — Catalog  *(auth: `unknown`)*
- **Details** — Detail / read-only view — Catalog  *(auth: `unknown`)*
- _2 more pages…_

---

## Most-Used User Controls

| Control | Purpose | Used By |
|---------|---------|---------|
| `ViewSwitcher.ascx` | ViewSwitcher reusable UI component | 0 pages |
| `ViewSwitcher.ascx` | ViewSwitcher reusable UI component | 0 pages |