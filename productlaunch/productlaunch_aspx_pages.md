# productlaunch — Page-by-Page Analysis

**5 pages** total.

---

## `ProductLaunch.Web/`  (5 pages)

### About.aspx

**File:** `ProductLaunch.Web\About.aspx`
**Purpose:** About page
**Functional Area:** Products
**Auth:** `anonymous`
**Page Title:** About
**Master Page:** `Site.Master`
**Code-Behind:** `ProductLaunch.Web.About` <- `About.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

### Contact.aspx

**File:** `ProductLaunch.Web\Contact.aspx`
**Purpose:** Contact page
**Functional Area:** Products
**Auth:** `anonymous`
**Page Title:** Contact
**Master Page:** `Site.Master`
**Code-Behind:** `ProductLaunch.Web.Contact` <- `Contact.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

### Default.aspx

**File:** `ProductLaunch.Web\Default.aspx`
**Purpose:** Application home page / dashboard
**Functional Area:** Products
**Auth:** `anonymous`
**Page Title:** Home Page
**Master Page:** `Site.Master`
**Code-Behind:** `ProductLaunch.Web._Default` <- `Default.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

### SignUp.aspx

**File:** `ProductLaunch.Web\SignUp.aspx`
**Purpose:** New user registration
**Functional Area:** Authentication
**Auth:** `anonymous`
**Page Title:** Sign Up
**Master Page:** `Site.Master`
**Code-Behind:** `ProductLaunch.Web.SignUp` <- `SignUp.aspx.cs`

**Controls (7):** 4× textbox, 2× dropdownlist, 1× button
**Flags:** Page_Load

**Handlers:** `Page_Load`, `btnGo_Click`

**Redirects / Transfers (1):**
- `ThankYou.aspx` *(transfer)*

### ThankYou.aspx

**File:** `ProductLaunch.Web\ThankYou.aspx`
**Purpose:** ThankYou page
**Functional Area:** Products
**Auth:** `unknown`
**Page Title:** Ta
**Master Page:** `Site.Master`
**Code-Behind:** `ProductLaunch.Web.ThankYou` <- `ThankYou.aspx.cs`
**Flags:** Page_Load

**Handlers:** `Page_Load`

---
