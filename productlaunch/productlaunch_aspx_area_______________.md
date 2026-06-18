# Authentication — Full Area Analysis

**1 pages** in this area.

Handles user identity: login, logout, registration, and password management.

Key pages: `SignUp.aspx`

---

## SignUp.aspx

**File:** `ProductLaunch.Web\SignUp.aspx`
**Purpose:** New user registration
**Functional Area:** Authentication
**Auth:** `anonymous`
**Page Title:** Sign Up
**Master Page:** `Site.Master`
**Code-Behind:** `ProductLaunch.Web.SignUp` <- `SignUp.aspx.cs`

**UI Controls (7):**
- textbox `#txtFirstName`
- textbox `#txtLastName`
- textbox `#txtEmail`
- dropdownlist `#ddlCountry`
- textbox `#txtCompanyName`
- dropdownlist `#ddlRole`
- button `#btnGo` — "Go!"
**Flags:** Page_Load
**Content Areas:** `MainContent`

**Event Handlers (2):**
- `Page_Load()`
- `btnGo_Click()`

**Namespaces (6):**
- `ProductLaunch.Model`
- `System`
- `System.Collections.Generic`
- `System.Linq`
- `System.Web.UI`
- `System.Web.UI.WebControls`

**Redirects / Transfers (1):**
- `ThankYou.aspx` *(transfer)*

---
