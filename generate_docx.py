import os
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_document():
    doc = docx.Document()
    
    # Page setup - Margins (0.75 inches on all sides)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    styles = doc.styles
    
    # Custom Document Styles (for headings and text outside mockups)
    title_style = styles.add_style('AppDocTitle', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    title_style.font.name = 'Arial'
    title_style.font.size = Pt(22)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor(30, 58, 138) # Dark Blue #1E3A8A
    
    desc_style = styles.add_style('AppDocDesc', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    desc_style.font.name = 'Arial'
    desc_style.font.size = Pt(10.5)
    desc_style.font.color.rgb = RGBColor(71, 85, 105) # Slate #475569
    
    h1_style = styles.add_style('AppH1', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    h1_style.font.name = 'Arial'
    h1_style.font.size = Pt(16)
    h1_style.font.bold = True
    h1_style.font.color.rgb = RGBColor(15, 23, 42) # Slate-900
    
    h2_style = styles.add_style('AppH2', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    h2_style.font.name = 'Arial'
    h2_style.font.size = Pt(12)
    h2_style.font.bold = True
    h2_style.font.color.rgb = RGBColor(51, 65, 85) # Slate-700
    
    # Add Cover Title
    p_title = doc.add_paragraph(style='AppDocTitle')
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p_title.add_run("MEDIPREP: HOSPITAL PROCEDURE PREPARATION SYSTEM\n")
    p_sub = doc.add_paragraph(style='AppDocDesc')
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.add_run("User Interface Form Designs & Screen Layout Mockups for MCA Project Submission\n\n\n\n\n\n")
    
    p_meta = doc.add_paragraph(style='AppDocDesc')
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.add_run("Submitted in partial fulfillment of project documentation requirements.\n")
    p_meta.add_run("Contains full visual mockups representing the structure, layouts, sections, validation guidelines, and input flows of all system screens.\n")
    doc.add_page_break()

    # Helper function to add a mockup page
    def add_mockup_page(page_name, description, mockup_text, show_page_break=True):
        doc.add_paragraph(page_name, style='AppH1')
        doc.add_paragraph(description, style='AppDocDesc')
        
        # Create single cell table for mockup frame
        table = doc.add_table(rows=1, cols=1)
        table.style = 'Table Grid'
        
        # Autoscale table to margins
        table.autofit = False
        table.columns[0].width = Inches(7.0)
        
        cell = table.cell(0, 0)
        cell.width = Inches(7.0)
        
        # Set background shading for cell to a light gray / slate color (#F8FAFC)
        shading_elm = parse_xml(r'<w:shd {} w:fill="F8FAFC"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading_elm)
        
        # Add layout mockup text
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.12
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Pt(6)
        p.paragraph_format.right_indent = Pt(6)
        
        run = p.add_run(mockup_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(8.5)
        run.font.bold = False
        run.font.color.rgb = RGBColor(15, 23, 42) # Slate-900
        
        if show_page_break:
            doc.add_page_break()

    # 1. Login Page
    login_mock = """+--------------------------------------------------------------------------+
|  MediPrep Portal | Secure Access Gateway                                 |
+--------------------------------------------------------------------------+
|                                                                          |
|                      HOSPITAL READINESS PORTAL                           |
|          Secure Authentication for Patients & Clinical Providers         |
|                                                                          |
|     +--------------------------------------------------------------+     |
|     |                                                              |     |
|     |  Username or Email Address                                   |     |
|     |  [ john.doe@patient.net                                    ] |     |
|     |  * Required field. Valid username or email format.           |     |
|     |                                                              |     |
|     |  Password                                                    |     |
|     |  [ ************                                            ] |     |
|     |  * Required field. Min 8 characters.                         |     |
|     |                                                              |     |
|     |                     +-----------------+                      |     |
|     |                     |     Sign In     |                      |     |
|     |                     +-----------------+                      |     |
|     +--------------------------------------------------------------+     |
|                                                                          |
|     Don't have an account? Register here                                 |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 1: Secure Login Screen",
        "Form Name: Secure User Login Form\n"
        "Purpose: Authenticate session access for all system actors (Admin, Doctor, Nurse, Patient).\n"
        "Validations: Mandatory checks on username/email and password; formatting requirements for email inputs.",
        login_mock
    )

    # 2. Dynamic Register Page
    register_mock = """+--------------------------------------------------------------------------+
|  MediPrep Portal | Secure User Registration                              |
+--------------------------------------------------------------------------+
|                                                                          |
|                          CREATE SECURE ACCOUNT                           |
|       Hospital Procedure Preparation & Clinical Readiness System         |
|                                                                          |
|  [ ACCOUNT CREDENTIALS ] ----------------------------------------------  |
|  Username:           [ patient_test_user                                ] |
|  * Required. Alphanumeric characters only.                               |
|  Email Address:      [ test.patient@hospital.org                        ] |
|  * Required. Valid email pattern required.                               |
|  Password:           [ StrongPass123!                                   ] |
|  * Required. Min 8 chars, 1 uppercase, 1 special character.              |
|  Confirm Password:   [ StrongPass123!                                   ] |
|  * Required. Must match Password field exactly.                          |
|                                                                          |
|  [ PERSONAL INFORMATION ] ---------------------------------------------  |
|  First Name:         [ Test                                             ] |
|  Last Name:          [ Patient                                          ] |
|  Phone Number:       [ +15559977                                        ] |
|  * Optional. Standard E.164 phone format.                                |
|  Access Group:       [ Patient                                      [v] ] |
|  * Required. Selection determines active subprofile fields below.        |
|                                                                          |
|  ======================================================================  |
|  [ DYNAMIC PROFILE: PATIENT CLINICAL PROFILE ] (Active)                  |
|  ======================================================================  |
|  Date of Birth:      [ 1995-04-12                                       ] |
|  * Required YYYY-MM-DD. Past dates only.                                 |
|  Gender:             [ Female                                       [v] ] |
|  * Required. Options: Male, Female, Other.                               |
|  Blood Group:        [ O+                                               ] |
|  * Optional. Max 5 chars.                                                |
|  Medical History:    [ None reported                                    ] |
|  * Optional text description of past medical conditions or allergies.    |
|  Emergency Contact:  [ Test Contact                                     ] |
|  * Required contact name.                                                |
|  Emergency Phone:    [ +15559988                                        ] |
|  * Required contact phone line.                                          |
|                                                                          |
|  ======================================================================  |
|  [ DYNAMIC PROFILE: CLINICAL PRACTITIONER CREDENTIALS ] (Hidden)         |
|  ======================================================================  |
|  Medical License:    [                                                  ] |
|  Specialization Area:[                                                  ] |
|  Clinical Dept:      [                                                  ] |
|                                                                          |
|  +--------------------+   +-------------------+                          |
|  |   Create Account   |   |   Back to Login   |                          |
|  +--------------------+   +-------------------+                          |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 2: Dynamic User Registration Screen",
        "Form Name: User Registration Form\n"
        "Purpose: Self-service account setup with dynamic role fields based on selected user type.\n"
        "Validations: Password confirmation checking, phone regex patterns, dynamic required states for conditional subprofiles.",
        register_mock
    )

    # 3. Admin Dashboard
    admin_dash_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Administrative Operations Dashboard           [ Welcome Admin ]|
+--------------------------------------------------------------------------+
|  [ Console Home ]  |  [ Clinicians ]  |  [ Patients ]  |  [ Templates ]  |
+--------------------------------------------------------------------------+
|                                                                          |
|                      ADMINISTRATIVE OPERATIONS CONTROL                   |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |  CLINICIAN DATABASE MANAGER                                      |   |
|   |  Register medical specialists, verify licensing numbers, and    |   |
|   |  maintain operational surgeon profiles in the system.            |   |
|   |                                                                  |   |
|   |  [ Manage Clinicians Directory ]                                 |   |
|   +------------------------------------------------------------------+   |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |  PATIENT REGISTRY MANAGEMENT                                     |   |
|   |  View active patients, audit clinical demographics, and update   |   |
|   |  emergency contacts and clinical history context.                |   |
|   |                                                                  |   |
|   |  [ Manage Patients Directory ]                                   |   |
|   +------------------------------------------------------------------+   |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |  PROCEDURE CATALOG TEMPLATES                                     |   |
|   |  Define CPT coding standards, category descriptions, and baseline|   |
|   |  operational durations for procedural setup.                     |   |
|   |                                                                  |   |
|   |  [ Manage Catalog Templates ]                                    |   |
|   +------------------------------------------------------------------+   |
|                                                                          |
|   System Environment Diagnostics:                                        |
|   Database Connection: [ OK ] | Active Clinicians: [ 8 ]                 |
|   Checklist Engine Status: [ Running ] | Pending Compliance Audits: [ 12 ]|
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 3: Administrative Dashboard Screen",
        "Form Name: Admin Operations Console\n"
        "Purpose: Central hub for administrators to route configuration paths and view diagnostic summaries.\n"
        "Navigation: Direct action links to clinician, patient, and procedure template directories.",
        admin_dash_mock
    )

    # 4. Admin - Doctors List
    admin_docs_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Clinician Registry                           |
+--------------------------------------------------------------------------+
|  [ Dashboard ]  |  [ Clinicians (Active) ]  |  [ Patients ]  |  [ Templates ] |
+--------------------------------------------------------------------------+
|                                                                          |
|                      SURGEON & CLINICIAN DIRECTORY                       |
|                                                                          |
|   [ + Register New Clinician ]     Search: [ Chen                      ] |
|                                                                          |
|   +----+--------------------+--------------+---------------+-------------+   |
|   | ID | Name               | Specialty    | License Code  | Department  |   |
|   +----+--------------------+--------------+---------------+-------------+   |
|   | 3  | Dr. Robert Chen    | Cardiology   | LIC-MD-99214  | Cardio Sci  |   |
|   | 7  | Dr. Sarah Jenkins  | Neurology    | LIC-MD-48201  | Neurosurg   |   |
|   | 11 | Dr. Alan Windsor   | Gastroenter  | LIC-MD-10822  | GI Medicine |   |
|   +----+--------------------+--------------+---------------+-------------+   |
|                                                                          |
|   Row Actions for [Dr. Robert Chen]:                                     |
|   +----------------------+   +-----------------------+                   |
|   | Edit Medical Profile |   | Deactivate Account   |                   |
|   +----------------------+   +-----------------------+                   |
|                                                                          |
|   [ Return to Operations Control ]                                       |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 4: Clinicians Directory Registry",
        "Form Name: Clinicians Directory List\n"
        "Purpose: Displays all registered clinician profiles, offering filtering and editing paths.\n"
        "Interactions: Search textbox filter, row actions selection (Edit Profile / Deactivate account).",
        admin_docs_mock
    )

    # 5. Admin - Add Clinician
    add_doc_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Add Clinician Profile                        |
+--------------------------------------------------------------------------+
|                                                                          |
|                          ADD CLINICIAN PROFILE                           |
|       Register login credentials and clinician profile metrics           |
|                                                                          |
|  [ ACCOUNT CREDENTIALS ] ----------------------------------------------  |
|  Username:           [ doctor_robert                                    ] |
|  * Required. Unique credential identifier.                               |
|  Password:           [ Password123!                                     ] |
|  * Required. Min 8 characters.                                           |
|  Email Address:      [ robert.surgeon@hospital.org                      ] |
|  * Required. Must match standard email formatting rules.                 |
|  Phone Number:       [ +15550102                                        ] |
|  * Optional. Contact number.                                             |
|                                                                          |
|  [ PERSONAL DETAILS ] -------------------------------------------------  |
|  First Name:         [ Robert                                           ] |
|  Last Name:          [ Chen                                             ] |
|  * Legal first name and family name fields.                              |
|                                                                          |
|  [ CLINICAL PROFILE INFO ] --------------------------------------------  |
|  Medical License:    [ LIC-MD-99214                                     ] |
|  * Required. Unique license number.                                      |
|  Specialty Focus:    [ Cardiology / Electrophysiology                   ] |
|  * Required. Area of practice.                                           |
|  Hospital Dept:      [ Cardiovascular Sciences                           ] |
|  * Required. Assigned hospital unit.                                     |
|                                                                          |
|  +---------------------------+   +--------------+                        |
|  |   Save Clinician Profile  |   |    Cancel    |                        |
|  +---------------------------+   +--------------+                        |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 5: Add Clinician Profile Form",
        "Form Name: Clinician Profile Form (Add Mode)\n"
        "Purpose: System administrator registers new medical clinician account and licensing info.\n"
        "Validations: Username uniqueness, password complexity, email formatting, and mandatory licensing checks.",
        add_doc_mock
    )

    # 6. Admin - Edit Clinician
    edit_doc_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Edit Clinician Profile                       |
+--------------------------------------------------------------------------+
|                                                                          |
|                          EDIT CLINICIAN PROFILE                          |
|             Update clinician account configuration and settings          |
|                                                                          |
|  [ ACCOUNT CREDENTIALS ] ----------------------------------------------  |
|  Email Address:      [ robert.surgeon@hospital.org                      ] |
|  * Required. Updates target contact email address.                       |
|  Phone Number:       [ +15550102                                        ] |
|  * Optional. Contact phone number.                                       |
|                                                                          |
|  [ PERSONAL DETAILS ] -------------------------------------------------  |
|  First Name:         [ Robert                                           ] |
|  Last Name:          [ Chen                                             ] |
|  * Names cannot be left empty.                                           |
|                                                                          |
|  [ CLINICAL PROFILE INFO ] --------------------------------------------  |
|  Medical License:    [ LIC-MD-99214                                     ] |
|  * Required. Read-only in database modification if restricted.           |
|  Specialty Focus:    [ Cardiology / Electrophysiology                   ] |
|  Hospital Dept:      [ Cardiovascular Sciences                           ] |
|                                                                          |
|  +---------------------------+   +--------------+                        |
|  |   Save Clinician Profile  |   |    Cancel    |                        |
|  +---------------------------+   +--------------+                        |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 6: Edit Clinician Profile Form",
        "Form Name: Clinician Profile Form (Edit Mode)\n"
        "Purpose: Update email, phone, specialty, and department for an existing clinician user (credentials hidden).\n"
        "Validations: Basic requirements remain active on email, first name, last name, and specialties.",
        edit_doc_mock
    )

    # 7. Admin - Patients List
    admin_pats_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Patient Registry                             |
+--------------------------------------------------------------------------+
|  [ Dashboard ]  |  [ Clinicians ]  |  [ Patients (Active) ]  |  [ Templates ]  |
+--------------------------------------------------------------------------+
|                                                                          |
|                          PATIENT DIRECTORY DATABASE                      |
|                                                                          |
|   Search: [ john.doe@patient.net                                       ] |
|                                                                          |
|   +----+-------------+------------+--------------------+-----------------+   |
|   | ID | Name        | DOB        | Email              | Emergency Line  |   |
|   +----+-------------+------------+--------------------+-----------------+   |
|   | 4  | John Doe    | 1980-05-15 | john.doe@patient.n | Jane (+1555999) |   |
|   | 5  | Alice Smith | 1992-11-23 | alice.smith@patien | David (+1555888)|   |
|   +----+-------------+------------+--------------------+-----------------+   |
|                                                                          |
|   Row Actions for [John Doe]:                                            |
|   +----------------------+                                               |
|   | Edit Patient Profile |                                               |
|   +----------------------+                                               |
|                                                                          |
|   [ Return to Operations Control ]                                       |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 7: Patient Directory Registry",
        "Form Name: Patient Registry Directory\n"
        "Purpose: Search, audit, and navigate to individual patient configurations.\n"
        "Interactions: Search filtering, direct edit navigations.",
        admin_pats_mock
    )

    # 8. Admin - Edit Patient
    edit_pat_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Edit Patient Profile                         |
+--------------------------------------------------------------------------+
|                                                                          |
|                          EDIT PATIENT PROFILE                            |
|             Update personal info and medical history metadata            |
|                                                                          |
|  [ ACCOUNT DETAILS ] --------------------------------------------------  |
|  Email Address:      [ john.doe@patient.net                             ] |
|  * Required. Valid email pattern.                                        |
|  Phone Number:       [ +15550103                                        ] |
|                                                                          |
|  [ PERSONAL DETAILS ] -------------------------------------------------  |
|  First Name:         [ John                                             ] |
|  Last Name:          [ Doe                                              ] |
|  Date of Birth:      [ 1980-05-15                                       ] |
|  Gender:             [ Male                                         [v] ] |
|  Blood Type:         [ A+                                               ] |
|                                                                          |
|  [ CLINICAL CONTEXT ] -------------------------------------------------  |
|  Medical History:    [ Hypertension, Mild Seasonal Allergies            ] |
|  * Historical conditions and allergies review area.                      |
|                                                                          |
|  [ EMERGENCY CONTACT ] ------------------------------------------------  |
|  Contact Name:       [ Jane Doe                                         ] |
|  * Required emergency contact person name.                               |
|  Contact Phone:      [ +15550999                                        ] |
|  * Required contact phone line.                                          |
|                                                                          |
|  +---------------------------+   +--------------+                        |
|  |   Save Patient Profile    |   |    Cancel    |                        |
|  +---------------------------+   +--------------+                        |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 8: Edit Patient Profile Form",
        "Form Name: Edit Patient Profile Form\n"
        "Purpose: Update demographics, emergency contacts, and medical history metrics for an existing patient user.\n"
        "Validations: Checks email syntax, contact phone codes, and date patterns.",
        edit_pat_mock
    )

    # 9. Admin - Procedure List
    admin_procs_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Catalog Templates                            |
+--------------------------------------------------------------------------+
|  [ Dashboard ]  |  [ Clinicians ]  |  [ Patients ]  |  [ Templates (Active) ] |
+--------------------------------------------------------------------------+
|                                                                          |
|                      PROCEDURE TEMPLATE CATALOG                          |
|                                                                          |
|   [ + Define New Template ]     Category: [ Cardiology               [v] ] |
|                                                                          |
|   +----+-----------+-----------------------------+-------------+---------+   |
|   | ID | CPT Code  | Procedure Name              | Category    | Duration|   |
|   +----+-----------+-----------------------------+-------------+---------+   |
|   | 1  | CPT-93452 | Left Heart Catheterization  | Cardiology  | 75 mins |   |
|   | 2  | CPT-45378 | Colonoscopy                 | Gastro      | 45 mins |   |
|   +----+-----------+-----------------------------+-------------+---------+   |
|                                                                          |
|   Row Actions for [Left Heart Catheterization]:                          |
|   +----------------------+                                               |
|   | Edit Template Specs  |                                               |
|   +----------------------+                                               |
|                                                                          |
|   [ Return to Operations Control ]                                       |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 9: Procedure Catalog Directory",
        "Form Name: Procedure Templates Catalog List\n"
        "Purpose: List baseline procedures, show categories, and select templates for editing.\n"
        "Interactions: Category dropdown filter, edit navigation action links.",
        admin_procs_mock
    )

    # 10. Admin - Add Procedure
    add_proc_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Define Procedure Template                     |
+--------------------------------------------------------------------------+
|                                                                          |
|                     DEFINE PROCEDURE CATALOG TEMPLATE                    |
|             Register CPT codes, category, and average duration           |
|                                                                          |
|  [ TEMPLATE METRICS ] -------------------------------------------------  |
|  CPT Code / ID:      [ CPT-93452                                        ] |
|  * Required. Alphanumeric CPT billing standard.                          |
|  Procedure Name:     [ Left Heart Catheterization                       ] |
|  * Required. Descriptive name of surgery template.                       |
|                                                                          |
|  [ CATEGORIZATION ] ---------------------------------------------------  |
|  Specialty Category: [ Cardiology                                       ] |
|  * Required. Specialty category name.                                    |
|  Estimated Duration: [ 75                                               ] |
|  * Required (Minutes). Value range 5 to 480 mins.                        |
|                                                                          |
|  [ CLINICAL DESCRIPTION ] ---------------------------------------------  |
|  Guidelines Summary: [ Diagnostic assessment of blood flow and pressure  |
|                        within chambers of the left heart.                ] |
|                                                                          |
|  +---------------------------+   +--------------+                        |
|  |    Save Catalog Item      |   |    Cancel    |                        |
|  +---------------------------+   +--------------+                        |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 10: Define Procedure Catalog Template Form",
        "Form Name: Procedure Template Form (Add Mode)\n"
        "Purpose: Create template models for specific operations including billing code definitions.\n"
        "Validations: CPT code structure, unique code checks, and estimated duration number bounds.",
        add_proc_mock
    )

    # 11. Admin - Edit Procedure
    edit_proc_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Admin Console | Edit Procedure Template                      |
+--------------------------------------------------------------------------+
|                                                                          |
|                     EDIT PROCEDURE CATALOG TEMPLATE                      |
|                 Modify template specifications and guidelines           |
|                                                                          |
|  [ TEMPLATE METRICS ] -------------------------------------------------  |
|  CPT Code / ID:      [ CPT-93452                                        ] |
|  * Code modification checks uniqueness on change.                        |
|  Procedure Name:     [ Left Heart Catheterization                       ] |
|                                                                          |
|  [ CATEGORIZATION ] ---------------------------------------------------  |
|  Specialty Category: [ Cardiology                                       ] |
|  Estimated Duration: [ 75                                               ] |
|  * Minutes duration (must be between 5 and 480).                         |
|                                                                          |
|  [ CLINICAL DESCRIPTION ] ---------------------------------------------  |
|  Guidelines Summary: [ Diagnostic assessment of blood flow and pressure  |
|                        within chambers of the left heart.                ] |
|                                                                          |
|  +---------------------------+   +--------------+                        |
|  |    Save Catalog Item      |   |    Cancel    |                        |
|  +---------------------------+   +--------------+                        |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 11: Edit Procedure Catalog Template Form",
        "Form Name: Procedure Template Form (Edit Mode)\n"
        "Purpose: Edit duration, guidelines description, and category details for a procedure template.\n"
        "Validations: Range checks on duration values.",
        edit_proc_mock
    )

    # 12. Doctor Dashboard
    doc_dash_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Physician Portal Control Center                 [ Dr. Robert ]|
+--------------------------------------------------------------------------+
|  [ Dashboard ]  |  [ + Schedule Surgery ]  |  [ Reports ]  |  [ Worklist ]  |
+--------------------------------------------------------------------------+
|                                                                          |
|                      PHYSICIAN OPERATIONS CONTROL CENTER                 |
|                                                                          |
|   Quick Navigation:                                                      |
|   [ + Schedule Surgery ]   [ Clinical Reports Center ]   [ Search Worklist ]|
|                                                                          |
|  ======================================================================  |
|  [ PRE-OP CLINICAL STATS & COMPLIANCE METRICS ]                          |
|  ======================================================================  |
|   Today's Cases: [ 1 ]             |  Patients Ready (Green):   [ 1 ]    |
|   Avg Compliance: [ 50% ]          |  Patients Warning (Yellow): [ 1 ]    |
|                                                                          |
|  ======================================================================  |
|  [ TODAY'S CASES ]                                                       |
|  ======================================================================  |
|   +--------------------+-----------+--------+---------------+----------+ |
|   | Patient            | CPT Code  | Time   | Readiness     | Action   | |
|   +--------------------+-----------+--------+---------------+----------+ |
|   | John Doe           | CPT-93452 | 09:00  | Warning (Yel) | [Manage] | |
|   +--------------------+-----------+--------+---------------+----------+ |
|                                                                          |
|  ======================================================================  |
|  [ UPCOMING SURGICAL SCHEDULES (Next 5 Cases) ]                          |
|  ======================================================================  |
|   +--------------------+-----------+-----------------+----------+------+ |
|   | Patient            | CPT Code  | Date            | Status   |Action| |
|   +--------------------+-----------+-----------------+----------+------+ |
|   | Alice Smith        | CPT-45378 | 2026-08-21 11:30|Scheduled |[Manage]|
|   +--------------------+-----------+-----------------+----------+------+ |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 12: Doctor Console Dashboard Screen",
        "Form Name: Physician Control Dashboard\n"
        "Purpose: Main workspace for surgeons to coordinate case schedules, track readiness compliance, and access reports.\n"
        "Interactions: Actions to schedule cases, review statistics, and manage pending checklist compliance.",
        doc_dash_mock
    )

    # 13. Doctor - Scheduled Procedures
    doc_sched_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Physician Portal | Scheduled Cases                           |
+--------------------------------------------------------------------------+
|  [ Dashboard ]  |  [ + Schedule Surgery ]  |  [ Reports ]  |  [ Worklist ]  |
+--------------------------------------------------------------------------+
|                                                                          |
|                          SURGICAL WORKLIST DIRECTORY                     |
|                                                                          |
|   Search: [ john.doe@patient.net                                       ] |
|                                                                          |
|   +-------------------+-----------------+-------------------+------------+   |
|   | Patient           | Procedure       | Scheduled Date    | Readiness  |   |
|   +-------------------+-----------------+-------------------+------------+   |
|   | John Doe          | Left Heart Cath | 2026-08-20 09:00  | Red (Alert)|   |
|   | Alice Smith       | Colonoscopy     | 2026-08-21 11:30  | Red (Alert)|   |
|   +-------------------+-----------------+-------------------+------------+   |
|                                                                          |
|   Row Actions for [John Doe]:                                            |
|   +------------------------+                                             |
|   | Manage Case Checklist  |                                             |
|   +------------------------+                                             |
|                                                                          |
|   [ Return to Portal Control ]                                           |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 13: Doctor Surgical Worklist Screen",
        "Form Name: Doctor Scheduled Procedures List\n"
        "Purpose: Audit view of active scheduled cases, mapping patients, dates, and color-coded readiness classifications.\n"
        "Interactions: Search filters and row action links to update cases and evaluate checklist items.",
        doc_sched_mock
    )

    # 14. Doctor - Schedule Surgery Add
    add_sched_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Physician Portal | Schedule Surgery                          |
+--------------------------------------------------------------------------+
|                                                                          |
|                          SCHEDULE SURGERY CASE                           |
|       Set up appointment details and customize preparation checklist     |
|                                                                          |
|  [ APPOINTMENT DETAILS ] ----------------------------------------------  |
|  Patient Account:    [ John Doe (john.doe@patient.net)              [v] ] |
|  * Required. Select target patient.                                      |
|  Procedure Type:     [ [CPT-93452] Left Heart Catheterization       [v] ] |
|  * Required. Baseline template checklist items will load on change.      |
|  Scheduled Time:     [ 2026-08-20T09:00                                 ] |
|  * Required. Future date and time.                                       |
|  OR Location:        [ Catheterization Lab 3                            ] |
|  * Required. Operating location.                                         |
|                                                                          |
|  [ CUSTOM PREPARATION CHECKLIST ITEMS ] -------------------------------  |
|  Configure tasks that the patient and staff must verify prior to surgery.|
|                                                                          |
|  +----------------------+------------+-------------+---------+-----------+ |
|  | Task Name            | Type       | Days Before | Critical| Action    | |
|  +----------------------+------------+-------------+---------+-----------+ |
|  | NPO Fasting          | PatientAct | 1           | [X]     | [Delete]  | |
|  | Stop Anticoagulant   | PatientAct | 2           | [X]     | [Delete]  | |
|  | Upload ECG Report    | DocUpload  | 3           | [X]     | [Delete]  | |
|  | Consent Signature    | StaffVerif | 0           | [X]     | [Delete]  | |
|  +----------------------+------------+-------------+---------+-----------+ |
|  [ + Add Custom Checklist Item ]                                         |
|                                                                          |
|  +--------------------+   +--------------+                               |
|  |   Save Schedule    |   |    Cancel    |                               |
|  +--------------------+   +--------------+                               |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 14: Schedule Surgery Case Form",
        "Form Name: Scheduled Procedure Configurator Form (Add Mode)\n"
        "Purpose: Setup appointments, link actors, and initialize/edit custom pre-op preparation checklist templates.\n"
        "Validations: Checks datetime fields for future schedules, requires valid target patient and CPT procedure selections.",
        add_sched_mock
    )

    # 15. Doctor - Edit Scheduled Surgery
    edit_sched_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Physician Portal | Edit Case & Compliance                     |
+--------------------------------------------------------------------------+
|                                                                          |
|                         EDIT SCHEDULED SURGERY CASE                      |
|                                                                          |
|  [ APPOINTMENT DETAILS ] ----------------------------------------------  |
|  Patient Account:    John Doe (john.doe@patient.net)   [Read-Only]       |
|  Procedure Type:     [CPT-93452] Left Heart Cath       [Read-Only]       |
|  Scheduled Time:     [ 2026-08-20T09:00                                 ] |
|  OR Location:        [ Catheterization Lab 3                            ] |
|  Case Status:        [ scheduled                                    [v] ] |
|                      Options: scheduled, completed, cancelled, delayed   |
|                                                                          |
|  [ ] Rebuild Preoperative Preparation Checklist                          |
|  * Warning: Overwrites active compliance results with template defaults. |
|                                                                          |
|  ======================================================================  |
|  [ ACTIVE PRE-OPERATIVE LAB METRICS & VITALS ]                           |
|  ======================================================================  |
|   Blood Sugar: 110.0 mg/dL | Hemoglobin: 14.0 g/dL | Body Temp: 98.6 °F  |
|   Creatinine:  0.9 mg/dL   | Blood Pressure: 120/80 mmHg                 |
|   ---------------------------------------------------------------------  |
|   Safety Alerts: (None) Vitals conform to pre-op safety thresholds.      |
|                                                                          |
|  ======================================================================  |
|  [ ACTIVE CHECKLIST COMPLIANCE STATUS & VERIFICATIONS ]                  |
|  ======================================================================  |
|  +--------------------+------------+------------+-----------+----------+ |
|  | Task Name          | Due Date   | Type       | Status    | Action   | |
|  +--------------------+------------+------------+-----------+----------+ |
|  | NPO Fasting        | 2026-08-20 | PatientAct | Pending   | Awaiting | |
|  | Stop Anticoagulant | 2026-08-18 | PatientAct | Completed | Verified | |
|  | Upload ECG Report  | 2026-08-17 | DocUpload  | Completed | [Approve]| |
|  | Clinical Consent   | 2026-08-20 | StaffVerif | Pending   | [Approve]| |
|  +--------------------+------------+------------+-----------+----------+ |
|                                                                          |
|  +--------------------+   +--------------+                               |
|  |   Save Schedule    |   |    Cancel    |                               |
|  +--------------------+   +--------------+                               |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 15: Edit Case & Verify Compliance Screen",
        "Form Name: Scheduled Procedure Configurator Form (Edit Mode)\n"
        "Purpose: Update appointment locations and times, review patient vitals and safety recommendations, and perform manual clinical sign-offs.\n"
        "Interactions: Verification triggers, status overrides, and checklist item sign-offs.",
        edit_sched_mock
    )

    # 16. Doctor - Reports Center
    reports_mock = """+--------------------------------------------------------------------------+
|  MediPrep | Physician Portal | Clinical Reports Center                   |
+--------------------------------------------------------------------------+
|  [ Dashboard ]  |  [ Clinicians ]  |  [ Patients ]  |  [ Reports (Active) ] |
+--------------------------------------------------------------------------+
|                                                                          |
|                          CLINICAL REPORTS CENTER                         |
|                                                                          |
|   Generate and export patient compliance checklists and safety summaries |
|                                                                          |
|   +------------------------------------------------------------------+   |
|   |  GENERATE COMPLIANCE REPORT                                      |   |
|   |                                                                  |   |
|   |  Patient Account:   [ John Doe (john.doe@patient.net)        [v] ]   |   |
|   |  * Selection pulls active scheduled surgeries for user.          |   |
|   |                                                                  |   |
|   |  Scheduled Case:    [ [2026-08-20] CPT-93452 - Left Heart    [v] ]   |   |
|   |                                                                  |   |
|   |  Export Format:     [ Adobe PDF Document (.pdf)              [v] ]   |   |
|   |                                                                  |   |
|   |  +-----------------------------+                                 |   |
|   |  |     Export System Report    |                                 |   |
|   |  +-----------------------------+                                 |   |
|   +------------------------------------------------------------------+   |
|                                                                          |
|   Historical Export Logs:                                                |
|   - ECG_Report_John_Doe.pdf (Generated 2026-07-29, 1.2MB)                |
|   - Pre-Op_Readiness_Report_Smith.pdf (Generated 2026-07-25, 342KB)      |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 16: Clinical Reports Center Screen",
        "Form Name: Clinical Report Generator Form\n"
        "Purpose: Generates and exports pre-operative checklist compliance certificates and safety summaries.\n"
        "Interactions: Dropdowns to specify target cases and formatting variables.",
        reports_mock
    )

    # 17. Patient Dashboard
    patient_dash_mock = """+--------------------------------------------------------------------------+
|  MediPrep | My Patient Care Space                        [ Welcome John ]|
+--------------------------------------------------------------------------+
|  [ Active Surgery Checklist ]  |  [ Message Board ]  |  [ Logout ]       |
+--------------------------------------------------------------------------+
|                                                                          |
|  🔔 PRE-OPERATIVE NOTIFICATIONS & SYSTEM REMINDERS                       |
|   - Fasting (NPO) required 8 hours prior to case.                        |
|   - Stop Anticoagulants (Blood Thinners) 48 hours prior to case.         |
|                                                                          |
|  ======================================================================  |
|  [ MY UPCOMING PROCEDURE APPOINTMENT ]                                   |
|  ======================================================================  |
|   Procedure: Left Heart Catheterization (CPT-93452)                      |
|   Scheduled: 2026-08-20 09:00 | Location: Catheterization Lab 3          |
|   Surgeon: Dr. Robert Chen | Department: Cardiovascular Sciences         |
|                                                                          |
|  ======================================================================  |
|  [ CLINICAL READINESS SUMMARY ]                                          |
|  ======================================================================  |
|   Compliance Status: [ Prep Warning (Yellow) ]                           |
|   Total Progress:    [=========== 50% Completed ============           ] |
|   Readiness Notes:   "Pending patient NPO verification and ECG review."  |
|                                                                          |
|  ======================================================================  |
|  [ PREOPERATIVE PREPARATION CHECKLIST ITEMS ]                            |
|  ======================================================================  |
|  +--------------------+------------+------------+-----------+----------+ |
|  | Task Name          | Due Date   | Type       | Status    | Action   | |
|  +--------------------+------------+------------+-----------+----------+ |
|  | NPO Fasting        | 2026-08-20 | PatientAct | Pending   | [Confirm]| |
|  | Stop Blood Thinners| 2026-08-18 | PatientAct | Completed | ✓ Done   | |
|  | Upload ECG Report  | 2026-08-17 | DocUpload  | Pending   | [Upload] | |
|  | Consent Form Sign  | 2026-08-20 | StaffVerif | Pending   | Awaiting | |
|  +--------------------+------------+------------+-----------+----------+ |
|                                                                          |
|  ======================================================================  |
|  [ RECORD PRE-OPERATIVE VITALS & LAB METRICS ]                           |
|  ======================================================================  |
|   Blood Sugar (mg/dL): [ 110.0 ]     Hemoglobin (g/dL): [ 14.0  ]        |
|   Temperature (°F):    [ 98.6  ]     Creatinine (mg/dL):[ 0.90  ]        |
|   BP Systolic (mmHg):  [ 120   ]     BP Diastolic(mmHg):[ 80    ]        |
|                                                                          |
|   +------------------------------------+                                 |
|   |  Save Vitals & Run Evaluation      |                                 |
|   +------------------------------------+                                 |
|                                                                          |
|  ======================================================================  |
|  [ PRE-OP GUIDELINES & SUGGESTIONS ]                                     |
|  ======================================================================  |
|  - Keep your cardiac device card (Pacemaker/ICD) on your person.         |
|                                                                          |
+--------------------------------------------------------------------------+"""
    add_mockup_page(
        "Page 17: Patient Dashboard Screen",
        "Form Name: Patient Preparation Care Space\n"
        "Purpose: Patient center to track preparation guidelines, upload records, complete checklists, log vitals, and read suggestions.\n"
        "Interactions: Vitals submission form, document upload trigger inputs, and notification listings.",
        patient_dash_mock,
        show_page_break=False
    )

    doc_filename = "MediPrep_Form_Designs.docx"
    doc.save(doc_filename)
    print(f"Word document saved to {doc_filename}")

if __name__ == "__main__":
    create_document()
