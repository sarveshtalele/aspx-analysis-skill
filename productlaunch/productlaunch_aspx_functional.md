# productlaunch — Functional View

**2 functional areas** covering all 5 pages.

---

## Authentication  (1 pages)

Handles user identity: login, logout, registration, and password management.

Key pages: `SignUp.aspx`

### SignUp.aspx

**Purpose:** New user registration  |  **Auth:** `anonymous`
**Controls:** 4× textbox, 2× dropdownlist, 1× button
**Handlers:** Page_Load, btnGo_Click
**Redirects to:** `ThankYou.aspx`
**Master:** `Site.Master`

---

## Products  (4 pages)

Product catalog management: listing, creation, editing, categorisation.

Key pages: `About.aspx`, `Contact.aspx`, `Default.aspx`, `ThankYou.aspx`

### About.aspx

**Purpose:** About page  |  **Auth:** `anonymous`
**Handlers:** Page_Load
**Master:** `Site.Master`

### Contact.aspx

**Purpose:** Contact page  |  **Auth:** `anonymous`
**Handlers:** Page_Load
**Master:** `Site.Master`

### Default.aspx

**Purpose:** Application home page / dashboard  |  **Auth:** `anonymous`
**Handlers:** Page_Load
**Master:** `Site.Master`

### ThankYou.aspx

**Purpose:** ThankYou page  |  **Auth:** `unknown`
**Handlers:** Page_Load
**Master:** `Site.Master`

---
