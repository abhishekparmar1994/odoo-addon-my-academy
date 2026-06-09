# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

start odoo

*Viewed [README.md](file:///c:/laragon/www/odoo/custom_addons/my_academy_modifications/README.md) *

*Listed directory [odoo](file:///c:/laragon/www/odoo) *

*Viewed [start.bat](file:///c:/laragon/www/odoo/start.bat) *

*Viewed [odoo.conf](file:///c:/laragon/www/odoo/odoo.conf) *

*User accepted the command `.\start.bat`*

### Planner Response

I have started the Odoo server in development mode.

Here is the status:
- **Port:** HTTP service is running on port **`8069`** (`http://localhost:8069` or `http://127.0.0.1:8069`).
- **Database:** Using the configuration `odoo@localhost:5432` with database `odoo`.
- **Addons Paths:** Loading addons from `server/addons` and `custom_addons`.
- **Mode:** Development mode with autoreload active (`--dev=all`).

### User Input

we have created custom addon now how to export it in how to import in new odoo

*User accepted the command `clear`*

*Grep searched codebase*

*Viewed [__manifest__.py](file:///c:/laragon/www/odoo/custom_addons/my_academy_modifications/__manifest__.py) *

### Planner Response

To export your custom addon and import/install it into a new Odoo instance, follow these steps:

---

## 📤 Part 1: How to Export the Custom Addon

Since an Odoo addon is just a folder containing Python code, XML views, and assets, exporting it simply involves packaging that folder:

1. **Locate the Addon Folder**:
   Go to your `custom_addons` directory in the current Odoo installation:
   * Path: `c:\laragon\www\odoo\custom_addons\my_academy_modifications`
2. **Package the Folder**:
   * Right-click the `my_academy_modifications` folder and select **Compress to ZIP file** (or use any archiving tool like 7-Zip).
   * Save it as `my_academy_modifications.zip`.
3. **Copy the File**:
   * Transfer the ZIP file (or the folder directly) to your target machine using USB, SSH/SFTP, Google Drive, or git.

---

## 📥 Part 2: How to Import it in a New Odoo Instance

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