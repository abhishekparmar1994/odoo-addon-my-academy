# Custom Addon Export & Import Guide

This guide explains how to export the **My Academy Webmyne** (`my_academy_modifications`) custom addon from this environment and import/install it into a new Odoo instance.

---

## 📤 Part 1: How to Export the Custom Addon

Since an Odoo addon is just a directory containing Python files, XML views, and configuration, exporting it is simple:

1. **Locate the Addon Folder**:
   Go to your `custom_addons` directory in this Odoo installation:
   * Path: `c:\laragon\www\odoo\custom_addons\my_academy_modifications`

2. **Package the Folder**:
   * Right-click the `my_academy_modifications` folder and select **Compress to ZIP file** (or use any archiving tool like 7-Zip).
   * Save it as `my_academy_modifications.zip`.

3. **Copy the File**:
   * Transfer the ZIP file (or the folder directly) to the target machine using USB, SFTP, git, or cloud storage.

---

## 📥 Part 2: How to Import & Install in a New Odoo Instance

Follow these steps to deploy and activate the addon in the new Odoo installation:

### Step 1: Place the Addon in the New Addons Directory
1. Transfer and extract your ZIP file onto the new server.
2. Locate the new Odoo installation's configuration file (usually named `odoo.conf`). Look at the `addons_path` variable:
   ```ini
   addons_path = /path/to/odoo/addons, /path/to/custom_addons
   ```
3. Copy the extracted `my_academy_modifications` folder directly into one of those configured folders (preferably a dedicated `/custom_addons` folder to keep it separate from Odoo's core modules).

### Step 2: Restart Odoo Server
For Odoo to detect the new folder on disk, you must restart the Odoo server process:
* **Windows (Laragon/Local)**: Run your startup script/batch file (like `start.bat`) or restart the Odoo service in Windows Services.
* **Linux/Ubuntu (Production)**: Run the service restart command:
  ```bash
  sudo systemctl restart odoo
  # or if running manually:
  ./odoo-bin -c odoo.conf
  ```

### Step 3: Install Core Dependencies
Ensure the standard Odoo modules that this addon depends on are already installed in the new Odoo database:
* **eLearning** (`website_slides`)
* **eLearning Certifications** (`website_slides_survey`)
* **eCommerce** (`website_sale`)
* **Sales** (`sale`)
* **eLearning eCommerce integration** (`website_sale_slides`)

*(For payment processing, also install the standard **Stripe** payment provider module via Apps).*

### Step 4: Register and Install the Custom Addon in the UI
1. Log in to the new Odoo database as an **Administrator**.
2. Activate **Developer Mode**:
   * Go to **Settings** → Scroll down to the bottom → Click **Activate the developer mode**.
3. Update Odoo's registry:
   * Navigate to the **Apps** app.
   * Click **Update Apps List** in the top navigation menu.
   * Confirm the dialog by clicking **Update**.
4. Install the module:
   * Clear the default **"Apps"** filter from the search bar (click the `x` on it).
   * Search for `my_academy_modifications` or `My Academy Webmyne`.
   * Click the **Activate** (or **Install**) button.
