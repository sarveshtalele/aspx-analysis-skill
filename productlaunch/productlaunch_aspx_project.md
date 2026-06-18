# productlaunch — ASP.NET Web Forms Application Analysis

> Generated: 2026-06-18T09:13:10.107049Z

---

## Executive Summary

This is an **ASP.NET Web Forms** application with **5 pages**, **1 user controls**, and **2 master pages** across **2 functional areas**.


---

## Codebase Metrics

| Metric | Count |
|--------|-------|
| ASPX Pages | 5 |
| User Controls (.ascx) | 1 |
| Master Pages | 2 |
| Functional Areas | 2 |
| Pages with Code-Behind | 5 |
| Pages using Master Page | 5 |
| Pages with AJAX (UpdatePanel) | 0 |
| Pages with Direct SQL | 0 |

---

## Access Control Breakdown

| Requirement | Pages |
|-------------|-------|
| `anonymous` | 4 |
| `unknown` | 1 |

---

## Master Pages

### `ProductLaunch.Web\Site.Master`
- **Purpose:** Layout master template
- **Used by:** 5 pages
- **Content Placeholders:** `MainContent`
- **ScriptManager (AJAX):** Yes

### `ProductLaunch.Web\Site.Mobile.Master`
- **Purpose:** Mobile layout template
- **Used by:** 0 pages
- **Content Placeholders:** `HeadContent`, `FeaturedContent`, `MainContent`

---

## Functional Areas Overview

### Authentication (1 page)
- **SignUp** — New user registration  *(auth: `anonymous`)*

### Products (4 pages)
- **About** — About page  *(auth: `anonymous`)*
- **Contact** — Contact page  *(auth: `anonymous`)*
- **Default** — Application home page / dashboard  *(auth: `anonymous`)*
- **ThankYou** — ThankYou page  *(auth: `unknown`)*

---

## Most-Used User Controls

| Control | Purpose | Used By |
|---------|---------|---------|
| `ViewSwitcher.ascx` | ViewSwitcher reusable UI component | 0 pages |