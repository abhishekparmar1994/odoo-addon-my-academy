# My Academy Webmyne (Custom eLearning Modifications)

A plug-and-play Odoo 19.0 module that integrates **lesson-gating**, **paid certificates**, and **Stripe payment checkout** for eLearning courses.

Developed by **Abhishek Parmar - Webmyne**.

---

## 🚀 Features

1. **Lesson-Completion Gate for Quizzes**
   - Students are blocked from taking a certification quiz until they have marked **all** prerequisite lessons in the course as completed.
   
2. **Paid Certificates**
   - Integrates Odoo's Survey/Certification model with eCommerce. 
   - A customizable **Certificate Product** field is added directly to Certification Surveys.
   - Automatically provisions a fallback certificate product on installation/upgrade.

3. **Stripe Checkout Flow**
   - Blocks the direct download of certificates until the student has purchased the associated certificate product.
   - Provides a beautiful, dedicated "Purchase Certificate" page with a direct checkout action.
   - Adds the product to the shopping cart and redirects the student instantly to `/shop/checkout` where Stripe handles the payment securely.

---

## 🛠️ Prerequisites

This module requires the following standard Odoo modules to be installed:
- `website_slides` (eLearning)
- `website_slides_survey` (eLearning Certifications)
- `website_sale` (eCommerce)
- `sale` (Sales Engine)

For payments, ensure that **Stripe** is installed and activated via Odoo's Payment Providers menu.

---

## 📦 Installation Instructions

1. **Upload / Extract the Module**
   - Extract the `my_academy_modifications.zip` archive.
   - Place the `my_academy_modifications` folder directly into your Odoo `custom_addons` directory.

2. **Restart Odoo Server**
   - Restart your Odoo server instance so Odoo detects the new custom addon.

3. **Update Apps List**
   - Log in to your Odoo instance as an **Administrator**.
   - Activate **Developer Mode** (via Settings).
   - Navigate to the **Apps** menu.
   - Click **Update Apps List** in the top navigation bar.

4. **Install the Addon**
   - Search for **"My Academy Webmyne"** or `my_academy_modifications`.
   - Click the **Install** button.

---

## ⚙️ Configuration & Setup

### 1. Stripe Payment Gateway Setup
- Navigate to **Website** → **Configuration** → **Payment Providers**.
- Select **Stripe** and toggle its state to **Enabled** or **Test Mode**.
- Enter your Stripe API credentials (Publishable Key and Secret Key) and save.

### 2. Linking Certificate Products to Surveys
- Go to the **Surveys** app or navigate to **Website** → **eLearning** → **Certifications**.
- Open a certification survey.
- Under the main form, locate the **Certificate Product** field.
- Select a product to link (e.g., "Webmyne Certification Fee"). If left empty on installation, the module automatically generates and links a default fallback product.

### 3. Add to eLearning Course
- Under eLearning, add the certification slide to the end of a course.
- The module will automatically handle all gates (blocking quiz start for incomplete lessons, blocking download for unpaid certificates) without any additional configuration!

---
*Proudly crafted for excellence in eLearning environments.*
