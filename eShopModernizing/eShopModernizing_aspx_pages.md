# eShopModernizing — Page-by-Page Analysis

**12 pages** total.

---

## `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms/`  (3 pages)

### About.aspx

**File:** `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\About.aspx`
**Purpose:** About page
**Functional Area:** Contact
**Auth:** `anonymous`
**Page Title:** About
**Master Page:** `Site.Master`
**Code-Behind:** `eShopLegacyWebForms.About` <- `About.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

### Contact.aspx

**File:** `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Contact.aspx`
**Purpose:** Contact page
**Functional Area:** Contact
**Auth:** `anonymous`
**Page Title:** Contact
**Master Page:** `Site.Master`
**Code-Behind:** `eShopLegacyWebForms.Contact` <- `Contact.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

### Default.aspx

**File:** `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Default.aspx`
**Purpose:** Application home page / dashboard
**Functional Area:** Home
**Auth:** `anonymous`
**Page Title:** Home Page
**Master Page:** `Site.Master`
**Code-Behind:** `eShopLegacyWebForms._Default` <- `Default.aspx.cs`

**Controls (1):** 1× listview
**Flags:** Page_Load

**Handlers:** `Page_Load`

---

## `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog/`  (4 pages)

### Create.aspx

**File:** `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Create.aspx`
**Purpose:** Create new Catalog
**Functional Area:** Products
**Auth:** `unknown`
**Page Title:** Create
**Master Page:** `Site.Master`
**Code-Behind:** `eShopLegacyWebForms.Catalog.Create` <- `Create.aspx.cs`

**Controls (14):** 6× textbox, 4× rangevalidator, 2× dropdownlist, 1× requiredfieldvalidator, 1× button
**Flags:** Page_Load

**Handlers:** `Page_Load`, `Create_Click`

**Redirects / Transfers (1):**
- `~` *(redirect)*

### Delete.aspx

**File:** `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Delete.aspx`
**Purpose:** Delete / remove confirmation — Catalog
**Functional Area:** Products
**Auth:** `unknown`
**Page Title:** Delete
**Master Page:** `Site.Master`
**Code-Behind:** `eShopLegacyWebForms.Catalog.Delete` <- `Delete.aspx.cs`

**Controls (1):** 1× button
**Flags:** Page_Load

**Handlers:** `Page_Load`, `Delete_Click`

**Redirects / Transfers (1):**
- `~` *(redirect)*

### Details.aspx

**File:** `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Details.aspx`
**Purpose:** Detail / read-only view — Catalog
**Functional Area:** Products
**Auth:** `unknown`
**Page Title:** Details
**Master Page:** `Site.Master`
**Code-Behind:** `eShopLegacyWebForms.Catalog.Details` <- `Details.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

### Edit.aspx

**File:** `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Edit.aspx`
**Purpose:** Edit / data entry form — Catalog
**Functional Area:** Products
**Auth:** `unknown`
**Page Title:** Edit
**Master Page:** `Site.Master`
**Code-Behind:** `eShopLegacyWebForms.Catalog.Edit` <- `Edit.aspx.cs`

**Controls (15):** 7× textbox, 4× rangevalidator, 2× dropdownlist, 1× requiredfieldvalidator, 1× button
**Flags:** Page_Load

**Handlers:** `Page_Load`, `Save_Click`

**Redirects / Transfers (1):**
- `~` *(redirect)*

---

## `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms/`  (1 pages)

### Default.aspx

**File:** `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Default.aspx`
**Purpose:** Application home page / dashboard
**Functional Area:** Home
**Auth:** `anonymous`
**Page Title:** Home Page
**Master Page:** `Site.Master`
**Code-Behind:** `eShopModernizedWebForms._Default` <- `Default.aspx.cs`

**Controls (1):** 1× listview
**Flags:** Page_Load

**Handlers:** `Page_Load`

---

## `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog/`  (4 pages)

### Create.aspx

**File:** `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Create.aspx`
**Purpose:** Create new Catalog
**Functional Area:** Products
**Auth:** `authenticated`
**Page Title:** Create
**Master Page:** `Site.Master`
**Code-Behind:** `eShopModernizedWebForms.Catalog.Create` <- `Create.aspx.cs`

**Controls (15):** 6× textbox, 4× rangevalidator, 2× dropdownlist, 1× hiddenfield, 1× requiredfieldvalidator, 1× button
**Flags:** Page_Load

**Handlers:** `Page_Load`, `Create_Click`

**Redirects / Transfers (1):**
- `~` *(redirect)*

### Delete.aspx

**File:** `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Delete.aspx`
**Purpose:** Delete / remove confirmation — Catalog
**Functional Area:** Products
**Auth:** `authenticated`
**Page Title:** Delete
**Master Page:** `Site.Master`
**Code-Behind:** `eShopModernizedWebForms.Catalog.Delete` <- `Delete.aspx.cs`

**Controls (1):** 1× button
**Flags:** Page_Load

**Handlers:** `Page_Load`, `Delete_Click`

**Redirects / Transfers (1):**
- `~` *(redirect)*

### Details.aspx

**File:** `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Details.aspx`
**Purpose:** Detail / read-only view — Catalog
**Functional Area:** Products
**Auth:** `unknown`
**Page Title:** Details
**Master Page:** `Site.Master`
**Code-Behind:** `eShopModernizedWebForms.Catalog.Details` <- `Details.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

### Edit.aspx

**File:** `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Edit.aspx`
**Purpose:** Edit / data entry form — Catalog
**Functional Area:** Products
**Auth:** `authenticated`
**Page Title:** Edit
**Master Page:** `Site.Master`
**Code-Behind:** `eShopModernizedWebForms.Catalog.Edit` <- `Edit.aspx.cs`

**Controls (16):** 7× textbox, 4× rangevalidator, 2× dropdownlist, 1× hiddenfield, 1× requiredfieldvalidator, 1× button
**Flags:** Page_Load

**Handlers:** `Page_Load`, `Save_Click`

**Redirects / Transfers (1):**
- `~` *(redirect)*

---
