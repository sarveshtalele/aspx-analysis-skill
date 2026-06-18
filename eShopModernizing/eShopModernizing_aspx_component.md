# eShopModernizing — Component Catalog

**4 master pages** | **2 user controls**

---

## Master Pages (4)

### `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Site.Master`

**Purpose:** Layout master template
**Used by:** 7 pages
**Content Placeholders:** `MainContent`
**AJAX:** Yes (ScriptManager)

**Pages using this master:**
- `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\About.aspx`
- `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Create.aspx`
- `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Delete.aspx`
- `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Details.aspx`
- `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Catalog\Edit.aspx`
- `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Contact.aspx`
- `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Default.aspx`

---

### `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Site.Master`

**Purpose:** Layout master template
**Used by:** 5 pages
**Content Placeholders:** `MainContent`
**Login Controls:** Yes (asp:Login / LoginView / LoginStatus)
**AJAX:** Yes (ScriptManager)

**Pages using this master:**
- `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Create.aspx`
- `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Delete.aspx`
- `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Details.aspx`
- `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Catalog\Edit.aspx`
- `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Default.aspx`

---

### `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\Site.Mobile.Master`

**Purpose:** Mobile layout template
**Used by:** 0 pages
**Content Placeholders:** `HeadContent`, `FeaturedContent`, `MainContent`
**Registered Controls:** ViewSwitcher.ascx

---

### `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\Site.Mobile.Master`

**Purpose:** Mobile layout template
**Used by:** 0 pages
**Content Placeholders:** `HeadContent`, `FeaturedContent`, `MainContent`
**Registered Controls:** ViewSwitcher.ascx

---

## User Controls (2)

### `eShopLegacyWebFormsSolution\src\eShopLegacyWebForms\ViewSwitcher.ascx`

**Purpose:** ViewSwitcher reusable UI component
**Used by:** 0 pages
**Class:** `eShopLegacyWebForms.ViewSwitcher`
**Event Handlers:** Page_Load

---

### `eShopModernizedWebFormsSolution\src\eShopModernizedWebForms\ViewSwitcher.ascx`

**Purpose:** ViewSwitcher reusable UI component
**Used by:** 0 pages
**Class:** `eShopModernizedWebForms.ViewSwitcher`
**Event Handlers:** Page_Load

---
