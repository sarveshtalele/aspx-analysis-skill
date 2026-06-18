# eShopModernizing — Functional View

**3 functional areas** covering all 12 pages.

---

## Contact  (2 pages)

User communication: contact forms, help, FAQ, feedback.

Key pages: `About.aspx`, `Contact.aspx`

### About.aspx

**Purpose:** About page  |  **Auth:** `anonymous`
**Handlers:** Page_Load
**Master:** `Site.Master`

### Contact.aspx

**Purpose:** Contact page  |  **Auth:** `anonymous`
**Handlers:** Page_Load
**Master:** `Site.Master`

---

## Home  (2 pages)

Application entry points: home page, landing pages, main dashboard.

Key pages: `Default.aspx`, `Default.aspx`

### Default.aspx

**Purpose:** Application home page / dashboard  |  **Auth:** `anonymous`
**Controls:** 1× listview
**Handlers:** Page_Load
**Master:** `Site.Master`

### Default.aspx

**Purpose:** Application home page / dashboard  |  **Auth:** `anonymous`
**Controls:** 1× listview
**Handlers:** Page_Load
**Master:** `Site.Master`

---

## Products  (8 pages)

Product catalog management: listing, creation, editing, categorisation.

Key pages: `Create.aspx`, `Create.aspx`, `Delete.aspx`, `Delete.aspx`, `Details.aspx` _+3 more_

### Create.aspx

**Purpose:** Create new Catalog  |  **Auth:** `unknown`
**Controls:** 6× textbox, 4× rangevalidator, 2× dropdownlist, 1× requiredfieldvalidator, 1× button
**Handlers:** Page_Load, Create_Click
**Redirects to:** `~`
**Master:** `Site.Master`

### Create.aspx

**Purpose:** Create new Catalog  |  **Auth:** `authenticated`
**Controls:** 6× textbox, 4× rangevalidator, 2× dropdownlist, 1× hiddenfield, 1× requiredfieldvalidator, 1× button
**Handlers:** Page_Load, Create_Click
**Redirects to:** `~`
**Master:** `Site.Master`

### Delete.aspx

**Purpose:** Delete / remove confirmation — Catalog  |  **Auth:** `unknown`
**Controls:** 1× button
**Handlers:** Page_Load, Delete_Click
**Redirects to:** `~`
**Master:** `Site.Master`

### Delete.aspx

**Purpose:** Delete / remove confirmation — Catalog  |  **Auth:** `authenticated`
**Controls:** 1× button
**Handlers:** Page_Load, Delete_Click
**Redirects to:** `~`
**Master:** `Site.Master`

### Details.aspx

**Purpose:** Detail / read-only view — Catalog  |  **Auth:** `unknown`
**Handlers:** Page_Load
**Master:** `Site.Master`

### Details.aspx

**Purpose:** Detail / read-only view — Catalog  |  **Auth:** `unknown`
**Handlers:** Page_Load
**Master:** `Site.Master`

### Edit.aspx

**Purpose:** Edit / data entry form — Catalog  |  **Auth:** `unknown`
**Controls:** 7× textbox, 4× rangevalidator, 2× dropdownlist, 1× requiredfieldvalidator, 1× button
**Handlers:** Page_Load, Save_Click
**Redirects to:** `~`
**Master:** `Site.Master`

### Edit.aspx

**Purpose:** Edit / data entry form — Catalog  |  **Auth:** `authenticated`
**Controls:** 7× textbox, 4× rangevalidator, 2× dropdownlist, 1× hiddenfield, 1× requiredfieldvalidator, 1× button
**Handlers:** Page_Load, Save_Click
**Redirects to:** `~`
**Master:** `Site.Master`

---
