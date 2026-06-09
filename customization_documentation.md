# 🛰️ Odoo 19 eLearning & Certification Customization Documentation
> **Enterprise Headless & Premium Monetization Suite for Odoo Custom Addon: `my_academy_modifications`**

This documentation provides an exhaustive, highly detailed technical and functional blueprint of the customization done for the Odoo custom addon `my_academy_modifications`. It is designed to be copied directly into Claude, ChatGPT, or any document generator to produce a professional, publication-ready Microsoft Word (.docx) file.

---

## 1. Executive Summary & Business Objectives

The **Antigravity eLearning Customization Suite** is an enterprise-grade extension designed for Odoo 19's `website_slides` and `website_slides_survey` modules. It bridges the gap between premium course content delivery and flexible certificate monetization. 

### Core Business Objectives:
*   **Flexible Course-Certificate Pricing Matrix**: Supports 4 distinct educational product models:
    1.  **Paid Course + Free Certificate**: A student pays a fee to enroll in the course; once enrolled, the certificate is unlocked for free upon passing.
    2.  **Free Course + Paid Certificate**: The course and its lessons are 100% free to audit, but downloading the official PDF certificate requires a Stripe checkout fee.
    
*   **Stunning Premium User Experience**: Replaces basic Odoo warning blocks and raw database `UserError` pages with immersive, highly aesthetic, modern glassmorphism web portals.
*   **Strict Lesson Completion Gates**: Enforces database and router-level constraints requiring students to complete every single lesson in a course before they are permitted to either start the certification quiz or download their PDF.

---

## 2. System Architecture & Model Extensions (`models/`)

To support multi-tenant scoping and flexible pricing structures, the addon extends Odoo's core database models with custom fields, validation methods, and interceptor hooks.

### 2.1. Survey Customizations (`models/survey_survey.py`)
Extends Odoo's `survey.survey` (certification quiz) model to support free certificate flags and custom product linkages:
*   **`certificate_is_free` (Boolean)**: Explicit flag indicating whether the certificate PDF is available for free without any payment check.
*   **`certificate_product_id` (Many2one ➔ `product.product`)**: Links a purchasable Odoo product (e.g., service variant) to the certificate.
*   **`_assign_missing_certificate_products()` (Method)**: Called programmatically on module upgrades to auto-link a fallback certificate product to any existing Odoo certification surveys (like Odoo's built-in demo courses) that don't have a product configured.

### 2.2. User Input & Scoring Validation (`models/survey_user_input.py`)
Overrides Odoo's `survey.user_input` (survey attempts) model to control the grading lifecycle and transactional congratulations emails:
*   **`certification_email_sent` (Boolean)**: Tracks whether the student has received their congratulatory email containing the PDF attachment.
*   **`_is_certificate_paid()` (Method)**: Core type-safe verification engine that checks if the active student has paid for the linked certificate.
    *   *Bypass*: Instantly returns `True` if `certificate_is_free` is checked.
    *   *Transactional Verification*: Queries `sale.order.line` to find a confirmed sales order (`state in ['sale', 'done']`) for the certificate product.
    *   *Stripe Dev Fallback*: If the order is in `draft` or `sent` state but has an authorized or completed Stripe transaction (`payment.transaction` in `['done', 'authorized']`), it is evaluated as successfully paid.
*   **`_mark_done()` (Overridden Method)**:
    *   Evaluates whether the congratulations email with the PDF certificate should be sent immediately or deferred.
    *   If the certificate requires payment and has not been purchased yet, the email is deferred. Once payment is completed, Odoo triggers the email dispatch.

### 2.3. Lesson Progress Validation (`models/slide_slide.py`)
Extends `slide.slide` to enforce structural gates:
*   **`get_uncompleted_lessons()` (Method)**:
    *   Natively queries all published slides (`is_published = True`) under the active course/channel, excluding the certification slide itself.
    *   Compares the slides against the active user's completed slide records (`slide.slide.partner`), returning a recordset of all remaining uncompleted lessons.

---

## 3. Controller Interceptors & Routing Gates (`controllers/main.py`)

A logic-rich controller layer acts as a headless gatekeeper, intercepting route requests and rendering premium custom interfaces instead of standard Odoo responses.

### 3.1. Quiz Start Controller (`/slides_survey/slide/get_certification_url`)
*   **Action**: Overrides Odoo's standard certification redirection endpoint.
*   **Logic**:
    1.  Fetches the certification slide details.
    2.  Calls `slide.get_uncompleted_lessons()`.
    3.  If uncompleted lessons exist, it blocks access and returns a custom rendered QWeb template (`my_academy_modifications.certification_locked_page`) instead of throwing an ugly `UserError` exception.
    4.  If all lessons are completed, it forwards the user to the native survey start page.

### 3.2. PDF Download & Stripe Redirection Controller (`/survey/<int:survey_id>/get_certification`)
*   **Action**: Intercepts Odoo's certification PDF generation endpoint.
*   **Logic**:
    1.  **Gate 1 (Attempt)**: Verifies if the student has passed the certification quiz.
    2.  **Gate 2 (Progress)**: Verifies if all lessons are completed (renders `certification_locked_page` if any lessons are missing).
    3.  **Gate 3 (Payment)**: Checks if the certificate is paid. If `certificate_is_free` is `False` and no sales order exists, it redirects the student to the dedicated payment portal page.
    4.  **Gate 4 (Delivery)**: Serves the compiled official PDF report.

### 3.3. Payment Portal & Cart Redirection
*   **`/academy/certificate/pay/<int:survey_id>`**: Renders a custom, high-end purchase landing page for the certificate, passing currency details, product prices, and benefits.
*   **`/academy/certificate/add-to-cart/<int:survey_id>`**: A secure POST endpoint that adds the certificate product to the Odoo checkout cart and immediately redirects the user to `/shop/checkout` where Stripe handles the payment.

---

## 4. Premium Front-End QWeb Templates (`views/`)

To provide an elite, modern aesthetic that drives brand value, custom QWeb templates were styled using harmonious color schemes, subtle micro-animations, and glassmorphism.

### 4.1. Certification Locked Page (`certification_locked_page`)
*   **Visual Highlights**: Styled with a professional crimson warning gradient (`linear-gradient(135deg, #e05252 0%, #d32f2f 100%)`) and sleek typography.
*   **Dynamic Breadcrumbs**: Includes a functional breadcrumb trail that reads directly from the active course channel name.
*   **Lessons Checklist**: Renders a list group where each remaining lesson is clearly highlighted with a play icon and a high-contrast **"Study Now"** action button directing students directly to the lesson content.
*   **Navigation**: Features a large, stylish return button at the bottom that takes the student back to the main course catalog.

### 4.2. Dedicated Payment landing Page (`certificate_payment_page`)
*   **Visual Highlights**: Styled with an elegant corporate blue gradient (`linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%)`).
*   **Value Proposition List**: Lists exact student benefits (personalized certificate, secure Stripe payment, instant PDF generation) utilizing clear checkmark icons.
*   **Price Card**: Displays a customized, green-themed transaction cost card outlining the total price in the active currency.
*   **Security Badges**: Includes trust seals and checkout badges for Visa, Mastercard, and Amex.

---

## 5. Course Catalog & Configuration Seeding (`scratch/`)

We implemented full-featured automated seeding scripts to programmatically populate the Odoo database with testing data and course scenarios.

| Course Model | Course Name | Enroll Policy | Price | Certificate Quiz | Certificate Type | Certificate Price |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Type 1** | *Professional Email Writing Course - level1 (Paid Course + Free Certificate)* | **On Payment** | $9.00 | Quiz 13 | **Free** | $0.00 |
| **Type 2** | *Professional Email Writing Course - level1 (Free Course + Paid Certificate)* | **Public / Free** | $0.00 | Quiz 14 | **Paid** | $15.00 |
| **Type 3** | *Professional Email Writing Course - level1 (Free Course + Free Certificate)* | **Public / Free** | $0.00 | Quiz 15 | **Free** | $0.00 |
| **Type 4** | *Professional Email Writing Course - level1 (Paid Course + Paid Certificate)* | **On Payment** | $9.00 | Quiz 16 | **Paid** | $15.00 |

---

## 6. Testing, Bug Fixing, and Quality Control

### 6.1. Transaction-Safe Integration Tests (`test_free_certification_flow.py`)
*   We developed an integration test suite that boots Odoo's environment natively in Python.
*   Runs isolated user mock transactions (enrolling, completing lessons, passing quizzes, validating cart checkout states).
*   Performs database rollbacks (`cr.rollback()`) to ensure no trash data persists in the production database.

### 6.2. Company Name & Logo QWeb Fallback Inheritance
*   **The Issue**: In standard Odoo, if a student completes a quiz while logged out (anonymous guest) or as a portal user, Odoo's standard PDF engine attempts to read the company logo from the student's user profile: `user_input.create_uid.sudo().company_id.logo`. Because guests and portal users do not have a standard corporate company linked, this value evaluates to `False`, rendering a **completely blank company name and company logo** on the generated certificate.
*   **The Resolution**: We inherited the QWeb certificate report view (`survey.certification_report_view_general`) in [`views/certificate_payment_templates.xml`](file:///c:/laragon/www/odoo/custom_addons/my_academy_modifications/views/certificate_payment_templates.xml) and added an intelligent fallback mechanism:
    *   It now automatically resolves the company to the **survey creator's company** first, and falls back to the **active website company** second: `user_input.survey_id.create_uid.sudo().company_id or user_input.env.company`.
    *   This guarantees that both the **Company Logo** and the **Company Name** are rendered 100% of the time, regardless of whether the user is logged in, logged out, or a guest!
