# MediPrep MCA Project Review – Redrawn Class Diagram Viva Speech Guide

**Project Title:** MediPrep – Hospital Procedure Preparation and Readiness System  
**Presented by:** Rynu Reji  
**Class:** S3 MCA | **Roll No:** 52  
**Guide:** Assistant Professor Rajesh A.V.  
**Presentation Deck:** `MediPrep_NEW_MCA_Review_Presentation.pptx`

---

## Class Diagram Explanation for Viva Review

> *"Respected guide Assistant Professor Rajesh A.V. and panel members, here is the redrawn UML Class Diagram for MediPrep."*

### Key Architectural Highlights:
1. **Central Entity**:  
   `ScheduledProcedure` is the central core class connecting `User` (patient & doctor) and `Procedure` (`User → ScheduledProcedure ← Procedure`).
2. **Removed Direct User–Procedure Line**:  
   There is **NO direct relationship line** between `User` and `Procedure`. Instead, a user books a `ScheduledProcedure`, which references a specific `Procedure` CPT catalog item.
3. **Clean 10-Class Relationships**:
   - `User` $\rightarrow$ `ScheduledProcedure`: `1` to `1..*` (A user can be linked to multiple procedure bookings as patient or doctor).
   - `Procedure` $\rightarrow$ `ScheduledProcedure`: `1` to `1..*` (A procedure catalog item can be scheduled multiple times).
   - `ScheduledProcedure` $\rightarrow$ `PatientVitals`: `1` to `0..*` (Logs patient pre-op vital parameters like sugar, BP, temperature).
   - `ScheduledProcedure` $\rightarrow$ `ChecklistItem`: `1` to `1..*` (Generates required pre-op compliance tasks).
   - `ChecklistItem` $\rightarrow$ `UploadedReport`: `1` to `0..1` (Links uploaded medical PDF files to checklist items).
   - `ScheduledProcedure` $\rightarrow$ `ProcedureReadiness`: `1` to `1` (Stores dynamic readiness percentage and status).
   - `ScheduledProcedure` $\rightarrow$ `RiskAlert`: `1` to `0..*` (Flags out-of-range vital safety warnings).
   - `Procedure` $\rightarrow$ `HealthSuggestion`: `1` to `0..*` (Provides CPT-specific guidelines).
   - `User` $\rightarrow$ `Notification`: `1` to `0..*` (Delivers direct doctor-patient board messages).
   - `ScheduledProcedure` $\rightarrow$ `Notification`: `1` to `0..*` (Links messages to procedure cases).

---

### 📂 Access Presentation Files:
* 📂 **[Download Updated PowerPoint Deck (`MediPrep_NEW_MCA_Review_Presentation.pptx`)](file:///C:/Users/acer/.gemini/antigravity/brain/58f1a014-bce9-4d5b-a1c3-b7c390f14c86/MediPrep_NEW_MCA_Review_Presentation.pptx)**
* 📂 **[Download Updated PowerPoint Deck (`MediPrep_MCA_Project_Review_Presentation.pptx`)](file:///c:/xampp/htdocs/hp$rs/antigravity/scratch/flask_auth_mvc/MediPrep_MCA_Project_Review_Presentation.pptx)**
* 📂 **[Download Speech Script (`mca_presentation_script.md`)](file:///c:/xampp/htdocs/hp$rs/antigravity/scratch/flask_auth_mvc/mca_presentation_script.md)**
