-- =========================================================================
-- Hospital Procedure Preparation and Readiness System - Seed Data Schema
-- Database Engine: InnoDB | Character Set: utf8mb4 | Collation: utf8mb4_unicode_ci
-- Indian Hospital Demo Version (Fortis Hospital Bangalore Case Model)
-- =========================================================================

CREATE DATABASE IF NOT EXISTS `hospital_readiness_db`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `hospital_readiness_db`;

-- Disable foreign key checks to prevent dependency ordering errors during drop
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `tbl_notifications`;
DROP TABLE IF EXISTS `tbl_risk_alerts`;
DROP TABLE IF EXISTS `tbl_health_suggestions`;
DROP TABLE IF EXISTS `tbl_procedure_readiness`;
DROP TABLE IF EXISTS `tbl_uploaded_reports`;
DROP TABLE IF EXISTS `tbl_checklist_items`;
DROP TABLE IF EXISTS `tbl_scheduled_procedures`;
DROP TABLE IF EXISTS `tbl_dynamic_checklist_templates`;
DROP TABLE IF EXISTS `tbl_procedures`;
DROP TABLE IF EXISTS `tbl_patient_vitals`;
DROP TABLE IF EXISTS `tbl_patient_profiles`;
DROP TABLE IF EXISTS `tbl_doctor_profiles`;
DROP TABLE IF EXISTS `tbl_users`;
DROP TABLE IF EXISTS `tbl_roles`;

SET FOREIGN_KEY_CHECKS = 1;

-- =========================================================================
-- Table 1: `tbl_roles`
-- =========================================================================
CREATE TABLE `tbl_roles` (
    `id` INT AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL,
    `description` VARCHAR(255) NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_role_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 2: `tbl_users`
-- =========================================================================
CREATE TABLE `tbl_users` (
    `id` INT AUTO_INCREMENT,
    `role_id` INT NOT NULL,
    `username` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `phone` VARCHAR(20) NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_username` (`username`),
    UNIQUE KEY `uq_email` (`email`),
    KEY `idx_user_role` (`role_id`),
    CONSTRAINT `fk_users_role` FOREIGN KEY (`role_id`) REFERENCES `tbl_roles` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 3: `tbl_doctor_profiles`
-- =========================================================================
CREATE TABLE `tbl_doctor_profiles` (
    `id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `license_number` VARCHAR(100) NOT NULL,
    `specialty` VARCHAR(100) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_doc_user` (`user_id`),
    UNIQUE KEY `uq_doc_license` (`license_number`),
    CONSTRAINT `fk_doc_user` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 4: `tbl_patient_profiles`
-- =========================================================================
CREATE TABLE `tbl_patient_profiles` (
    `id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `date_of_birth` DATE NOT NULL,
    `gender` ENUM('male', 'female', 'other') NOT NULL,
    `blood_type` VARCHAR(5) NULL,
    `medical_history` TEXT NULL,
    `emergency_contact_name` VARCHAR(100) NOT NULL,
    `emergency_contact_phone` VARCHAR(20) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_pat_user` (`user_id`),
    CONSTRAINT `fk_pat_user` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 5: `tbl_procedures`
-- =========================================================================
CREATE TABLE `tbl_procedures` (
    `id` INT AUTO_INCREMENT,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT NULL,
    `category` VARCHAR(50) NOT NULL,
    `est_duration_mins` INT NOT NULL DEFAULT 60,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_proc_code` (`code`),
    KEY `idx_proc_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 5b: `tbl_dynamic_checklist_templates`
-- =========================================================================
CREATE TABLE `tbl_dynamic_checklist_templates` (
    `id` INT AUTO_INCREMENT,
    `procedure_id` INT NOT NULL,
    `task_name` VARCHAR(100) NOT NULL,
    `task_type` ENUM('patient_action', 'staff_verification', 'document_upload') NOT NULL,
    `description` TEXT NULL,
    `due_days_before` INT NOT NULL DEFAULT 1,
    `is_critical` BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (`id`),
    KEY `idx_template_proc` (`procedure_id`),
    CONSTRAINT `fk_template_proc` FOREIGN KEY (`procedure_id`) REFERENCES `tbl_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 6: `tbl_scheduled_procedures`
-- =========================================================================
CREATE TABLE `tbl_scheduled_procedures` (
    `id` INT AUTO_INCREMENT,
    `patient_id` INT NOT NULL,
    `doctor_id` INT NOT NULL,
    `procedure_id` INT NOT NULL,
    `scheduled_at` DATETIME NOT NULL,
    `location` VARCHAR(100) NOT NULL,
    `status` ENUM('scheduled', 'completed', 'cancelled', 'delayed') NOT NULL DEFAULT 'scheduled',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_sched_time` (`scheduled_at`),
    KEY `idx_sched_patient` (`patient_id`),
    KEY `idx_sched_doctor` (`doctor_id`),
    CONSTRAINT `fk_sched_patient` FOREIGN KEY (`patient_id`) REFERENCES `tbl_users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_sched_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `tbl_users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_sched_proc` FOREIGN KEY (`procedure_id`) REFERENCES `tbl_procedures` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 7: `tbl_checklist_items`
-- =========================================================================
CREATE TABLE `tbl_checklist_items` (
    `id` INT AUTO_INCREMENT,
    `scheduled_procedure_id` INT NOT NULL,
    `task_name` VARCHAR(100) NOT NULL,
    `task_type` ENUM('patient_action', 'staff_verification', 'document_upload') NOT NULL,
    `description` TEXT NULL,
    `due_by_datetime` DATETIME NOT NULL,
    `is_critical` BOOLEAN NOT NULL DEFAULT FALSE,
    `status` ENUM('pending', 'completed', 'verified', 'failed') NOT NULL DEFAULT 'pending',
    `completed_by_user_id` INT NULL,
    `completed_at` DATETIME NULL,
    `verified_by_user_id` INT NULL,
    `verified_at` DATETIME NULL,
    `notes` TEXT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_item_sched` (`scheduled_procedure_id`),
    KEY `idx_item_due` (`due_by_datetime`),
    CONSTRAINT `fk_item_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_item_completed_by` FOREIGN KEY (`completed_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_item_verified_by` FOREIGN KEY (`verified_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 8: `tbl_uploaded_reports`
-- =========================================================================
CREATE TABLE `tbl_uploaded_reports` (
    `id` INT AUTO_INCREMENT,
    `checklist_item_id` INT NOT NULL,
    `file_name` VARCHAR(255) NOT NULL,
    `file_path` VARCHAR(512) NOT NULL,
    `file_size_bytes` INT NOT NULL,
    `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_report_item` (`checklist_item_id`),
    CONSTRAINT `fk_report_item` FOREIGN KEY (`checklist_item_id`) REFERENCES `tbl_checklist_items` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 9: `tbl_procedure_readiness`
-- =========================================================================
CREATE TABLE `tbl_procedure_readiness` (
    `id` INT AUTO_INCREMENT,
    `scheduled_procedure_id` INT NOT NULL,
    `readiness_status` ENUM('red', 'orange', 'yellow', 'green') NOT NULL DEFAULT 'red',
    `evaluated_by_user_id` INT NULL,
    `last_evaluated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `notes` TEXT NULL,
    `override_reason` TEXT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_readiness_sched` (`scheduled_procedure_id`),
    CONSTRAINT `fk_readiness_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_readiness_eval_by` FOREIGN KEY (`evaluated_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 10: `tbl_health_suggestions`
-- =========================================================================
CREATE TABLE `tbl_health_suggestions` (
    `id` INT AUTO_INCREMENT,
    `procedure_id` INT NOT NULL,
    `suggestion_text` TEXT NOT NULL,
    `trigger_condition` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_sugg_proc` (`procedure_id`),
    CONSTRAINT `fk_sugg_proc` FOREIGN KEY (`procedure_id`) REFERENCES `tbl_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 11: `tbl_risk_alerts`
-- =========================================================================
CREATE TABLE `tbl_risk_alerts` (
    `id` INT AUTO_INCREMENT,
    `scheduled_procedure_id` INT NOT NULL,
    `alert_type` VARCHAR(100) NOT NULL,
    `alert_message` TEXT NOT NULL,
    `severity` ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    `is_resolved` BOOLEAN NOT NULL DEFAULT FALSE,
    `resolved_by_user_id` INT NULL,
    `resolved_at` DATETIME NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_alert_sched` (`scheduled_procedure_id`),
    KEY `idx_alert_resolved` (`is_resolved`),
    CONSTRAINT `fk_alert_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_alert_resolved_by` FOREIGN KEY (`resolved_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 12: `tbl_notifications`
-- =========================================================================
CREATE TABLE `tbl_notifications` (
    `id` INT AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `sender_id` INT NULL,
    `scheduled_procedure_id` INT NULL,
    `title` VARCHAR(150) NOT NULL,
    `message` TEXT NOT NULL,
    `type` ENUM('sms', 'email', 'in_app') NOT NULL DEFAULT 'in_app',
    `status` ENUM('unread', 'read', 'failed') NOT NULL DEFAULT 'unread',
    `sent_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_notif_user` (`user_id`),
    KEY `idx_notif_status` (`status`),
    CONSTRAINT `fk_notif_user` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_notif_sender` FOREIGN KEY (`sender_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_notif_procedure` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- Table 13: `tbl_patient_vitals`
-- =========================================================================
CREATE TABLE `tbl_patient_vitals` (
    `id` INT AUTO_INCREMENT,
    `scheduled_procedure_id` INT NOT NULL,
    `blood_sugar` DECIMAL(5,2) NULL,
    `hemoglobin` DECIMAL(4,2) NULL,
    `systolic_bp` INT NULL,
    `diastolic_bp` INT NULL,
    `temperature` DECIMAL(4,1) NULL,
    `creatinine` DECIMAL(4,2) NULL,
    `recorded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_vitals_sched` (`scheduled_procedure_id`),
    CONSTRAINT `fk_vitals_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================================
-- SEED DATA SETUP
-- =========================================================================

-- 1. Seed Roles
INSERT INTO `tbl_roles` (`id`, `name`, `description`) VALUES
(1, 'admin', 'System Administrator with infrastructure and template access'),
(3, 'doctor', 'Attending Surgeon performing tbl_procedures'),
(4, 'patient', 'The patient undergoing the medical procedure');

-- 2. Seed Users (Bcrypt hashes: admin123, doctor123, patient123)
INSERT INTO `tbl_users` (`id`, `role_id`, `username`, `email`, `password_hash`, `first_name`, `last_name`, `phone`, `is_active`) VALUES
-- Admins (Role 1)
(1, 1, 'admin_priya', 'priya.nair@fortis.in', '$2b$12$sl2gMR2fmfBbCnQ7MfWsjeXwZmWiR3TpFz9uJfrRTTLFbvNTa30/y', 'Priya', 'Nair', '+919876543210', 1),
(2, 1, 'admin_rajesh', 'rajesh.gupta@fortis.in', '$2b$12$sl2gMR2fmfBbCnQ7MfWsjeXwZmWiR3TpFz9uJfrRTTLFbvNTa30/y', 'Rajesh', 'Gupta', '+919876543211', 1),
-- Doctors (Role 3)
(3, 3, 'doctor_robert', 'anil.sharma@fortis.in', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Anil', 'Sharma', '+919876543212', 1),
(4, 3, 'doctor_patel', 'amit.patel@fortis.in', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Amit', 'Patel', '+919876543213', 1),
(5, 3, 'doctor_iyer', 'raman.iyer@fortis.in', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Raman', 'Iyer', '+919876543214', 1),
(6, 3, 'doctor_reddy', 'kiran.reddy@fortis.in', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Kiran', 'Reddy', '+919876543215', 1),
(7, 3, 'doctor_menon', 'suresh.menon@fortis.in', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Suresh', 'Menon', '+919876543216', 1),
-- Patients (Role 4)
(8, 4, 'patient_john', 'amit.kumar@gmail.com', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Amit', 'Kumar', '+919810012345', 1),
(9, 4, 'patient_sunita', 'sunita.rao@yahoo.co.in', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Sunita', 'Rao', '+919820012345', 1),
(10, 4, 'patient_rahul', 'rahul.verma@gmail.com', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Rahul', 'Verma', '+919830012345', 1),
(11, 4, 'patient_ananya', 'ananya.sen@gmail.com', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Ananya', 'Sen', '+919840012345', 1),
(12, 4, 'patient_vikram', 'vikram.singh@gmail.com', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Vikram', 'Singh', '+919850012345', 1),
(13, 4, 'patient_karan', 'karan.johri@gmail.com', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Karan', 'Johri', '+919860012345', 1),
(14, 4, 'patient_meera', 'meera.desai@gmail.com', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Meera', 'Desai', '+919870012345', 1),
(15, 4, 'patient_rohan', 'rohan.kapoor@gmail.com', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Rohan', 'Kapoor', '+919880012345', 1);

-- 3. Seed Doctor Profiles
INSERT INTO `tbl_doctor_profiles` (`id`, `user_id`, `license_number`, `specialty`, `department`) VALUES
(1, 3, 'KMC-88123', 'Cardiology / Electrophysiology', 'Cardiovascular Sciences'),
(2, 4, 'KMC-42901', 'Orthopedic Surgery', 'Bone & Joint Institute'),
(3, 5, 'KMC-30822', 'Gastroenterology', 'GI Sciences Unit'),
(4, 6, 'KMC-11928', 'Neurology & Neurosurgery', 'Brain & Spine Care'),
(5, 7, 'KMC-54310', 'Surgical Oncology', 'Cancer Care Center');

-- 4. Seed Patient Profiles
INSERT INTO `tbl_patient_profiles` (`id`, `user_id`, `date_of_birth`, `gender`, `blood_type`, `medical_history`, `emergency_contact_name`, `emergency_contact_phone`) VALUES
(1, 8, '1980-05-15', 'male', 'A+', 'Hypertension (managed), seasonal dust allergies', 'Jane Kumar', '+919810054321'),
(2, 9, '1992-11-23', 'female', 'O-', 'Type-2 Diabetes (Metformin 500mg daily)', 'David Rao', '+919820054321'),
(3, 10, '1965-02-10', 'male', 'B+', 'Chronic Gastritis, past knee arthroscopy (2018)', 'Kiran Verma', '+919830054321'),
(4, 11, '1988-08-04', 'female', 'O+', 'Mild Asthma (inhaler SOS)', 'Arup Sen', '+919840054321'),
(5, 12, '1974-12-30', 'male', 'AB+', 'No major pre-existing conditions reported', 'Sita Singh', '+919850054321'),
(6, 13, '1995-07-21', 'male', 'A-', 'G6PD Deficiency', 'Sunil Johri', '+919860054321'),
(7, 14, '1959-10-18', 'female', 'B-', 'Hypothyroidism (Thyronorm 75mcg daily)', 'Neeraj Desai', '+919870054321'),
(8, 15, '2001-04-03', 'male', 'O+', 'None reported', 'Kailash Kapoor', '+919880054321');

-- 5. Seed Procedures
INSERT INTO `tbl_procedures` (`id`, `code`, `name`, `description`, `category`, `est_duration_mins`) VALUES
(1, 'CPT-93452', 'Left Heart Catheterization', 'Diagnostic cardiac catheterization to evaluate coronary arteries and left ventricles.', 'Cardiology', 75),
(2, 'CPT-27447', 'Total Knee Arthroplasty', 'Replacement of the damaged knee joint surface with metallic and plastic implants.', 'Orthopedics', 120),
(3, 'CPT-45378', 'Diagnostic Colonoscopy', 'Endoscopic visualization of the colon and distal small bowel for screening or diagnosis.', 'Gastroenterology', 45),
(4, 'CPT-66984', 'Cataract Surgery with IOL', 'Removal of clouding eye lens and implantation of intraocular lens.', 'Ophthalmology', 30),
(5, 'CPT-47562', 'Laparoscopic Cholecystectomy', 'Minimally invasive removal of the gallbladder due to gallstones.', 'General Surgery', 60),
(6, 'CPT-52601', 'Transurethral Resection of Prostate', 'Endoscopic surgical removal of prostate tissue blocking urine flow.', 'Urology', 90);

-- 5b. Seed Dynamic Checklist Templates
INSERT INTO `tbl_dynamic_checklist_templates` (`procedure_id`, `task_name`, `task_type`, `description`, `due_days_before`, `is_critical`) VALUES
-- Left Heart Catheterization
(1, 'NPO Fasting (No food or water)', 'patient_action', 'Strict fasting required for at least 8 hours prior to the catheterization.', 1, 1),
(1, 'Stop Anticoagulant (Blood Thinners)', 'patient_action', 'Temporarily suspend blood thinners 48 hours prior as advised by physician.', 2, 1),
(1, 'Upload Recent ECG Lab Report', 'document_upload', 'Please upload a PDF scan of your 12-lead ECG conducted in the last 14 days.', 3, 1),
(1, 'Clinical Consent Form Signature', 'patient_action', 'Verify that the physical surgical consent documentation has been signed.', 0, 1),
-- Knee Arthroplasty
(2, 'Pre-operative Joint Cleansing Prep', 'patient_action', 'Wash the target knee with chlorhexidine scrub on the night before and morning of surgery.', 1, 0),
(2, 'Verify Blood Group Compatibility & Match', 'staff_verification', 'Ensure 2 units of matched packed red blood cells are reserved in the blood bank.', 1, 1),
(2, 'Upload Knee X-Ray & MRI Scans', 'document_upload', 'Upload high-resolution scans of the target knee joint.', 5, 1),
(2, 'Discontinue NSAIDs / Blood Thinners', 'patient_action', 'Stop taking aspirin, ibuprofen, or other anti-inflammatories 7 days before.', 7, 1),
-- Colonoscopy
(3, 'Liquid Prep Diet Compliance', 'patient_action', 'Complete the PEG bowel preparation formulation starting 24 hours prior.', 1, 1),
(3, 'Confirm Escort Driver Present', 'patient_action', 'Provide details of the responsible adult driving you home after sedation.', 0, 0),
(3, 'Sign Colonoscopy Consent Form', 'patient_action', 'Check signed physical procedure authorization forms.', 0, 1),
-- Cataract
(4, 'Initiate Pre-op Antibiotic Drops', 'patient_action', 'Apply prescribed eye drops 3 times daily starting 3 days before.', 3, 0),
(4, 'Fasting (NPO)', 'patient_action', 'No heavy meals or liquids 6 hours before the local anesthesia.', 1, 1),
-- Cholecystectomy
(5, 'Upload Blood Sugar / HbA1c Profile', 'document_upload', 'Provide recent blood test results (less than 7 days old).', 3, 1),
(5, 'Fasting (NPO)', 'patient_action', 'Strict fasting from midnight before the general anesthesia.', 1, 1);

-- 6. Seed Scheduled Procedures
INSERT INTO `tbl_scheduled_procedures` (`id`, `patient_id`, `doctor_id`, `procedure_id`, `scheduled_at`, `location`, `status`) VALUES
(1, 8, 3, 1, '2026-09-24 09:00:00', 'Catheterization Lab 3', 'scheduled'),
(2, 9, 3, 1, '2026-09-25 11:30:00', 'Catheterization Lab 3', 'scheduled'),
(3, 10, 4, 2, '2026-08-12 08:30:00', 'OR Suite 2 (Orthopedics)', 'scheduled'),
(4, 11, 5, 3, '2026-08-14 14:00:00', 'Endoscopy Suite B', 'scheduled'),
(5, 12, 5, 3, '2026-08-14 15:30:00', 'Endoscopy Suite B', 'scheduled'),
(6, 13, 6, 4, '2026-08-15 10:00:00', 'Day Care Eye OR 1', 'scheduled'),
(7, 14, 7, 5, '2026-08-18 09:00:00', 'General Surgery OR 5', 'scheduled'),
(8, 15, 3, 1, '2026-08-20 09:00:00', 'Catheterization Lab 1', 'scheduled');

-- 6b. Seed Patient Vitals
INSERT INTO `tbl_patient_vitals` (`id`, `scheduled_procedure_id`, `blood_sugar`, `hemoglobin`, `systolic_bp`, `diastolic_bp`, `temperature`, `creatinine`) VALUES
(1, 1, 110.0, 14.5, 125, 82, 98.4, 0.90),
(2, 2, 175.0, 11.2, 145, 95, 99.1, 1.20), -- Diabetic patient Sunita, elevated values
(3, 3, 98.5, 13.8, 130, 85, 98.6, 0.85),
(4, 4, 105.2, 12.5, 118, 78, 98.0, 0.75),
(5, 5, 112.0, 15.0, 120, 80, 98.4, 0.95),
(7, 7, 135.0, 10.5, 150, 92, 100.2, 1.40); -- Elevated temp/creatinine for patient Meera

-- 7. Seed Checklist Items
INSERT INTO `tbl_checklist_items` (`id`, `scheduled_procedure_id`, `task_name`, `task_type`, `description`, `due_by_datetime`, `is_critical`, `status`) VALUES
-- Schedule 1 (Amit Kumar - Cardiac)
(1, 1, 'NPO Fasting (No food or water)', 'patient_action', 'Strict fasting required for at least 8 hours.', '2026-09-24 01:00:00', 1, 'completed'),
(2, 1, 'Stop Anticoagulant (Blood Thinners)', 'patient_action', 'Temporarily suspend blood thinners 48 hours prior.', '2026-09-22 09:00:00', 1, 'completed'),
(3, 1, 'Upload Recent ECG Lab Report', 'document_upload', 'Upload recent ECG.', '2026-09-21 17:00:00', 1, 'pending'),
(4, 1, 'Clinical Consent Form Signature', 'patient_action', 'Surgical consent confirmation.', '2026-09-24 08:30:00', 1, 'verified'),
-- Schedule 2 (Sunita Rao - Cardiac)
(5, 2, 'NPO Fasting (No food or water)', 'patient_action', 'Fasting required.', '2026-09-24 18:00:00', 1, 'pending'),
(6, 2, 'Stop Anticoagulant (Blood Thinners)', 'patient_action', 'Suspend thinners.', '2026-09-25 10:30:00', 1, 'completed'),
(7, 2, 'Upload Recent ECG Lab Report', 'document_upload', 'Upload ECG report.', '2026-08-07 17:00:00', 1, 'pending'),
(8, 2, 'Clinical Consent Form Signature', 'patient_action', 'Surgical consent confirmation.', '2026-08-10 11:00:00', 1, 'pending'),
-- Schedule 3 (Rahul Verma - Knee)
(9, 3, 'Pre-operative Joint Cleansing Prep', 'patient_action', 'Wash target knee.', '2026-08-11 20:00:00', 0, 'completed'),
(10, 3, 'Verify Blood Group Compatibility & Match', 'staff_verification', 'Verify blood bank reservation.', '2026-08-11 08:30:00', 1, 'verified'),
(11, 3, 'Upload Knee X-Ray & MRI Scans', 'document_upload', 'Upload joint images.', '2026-08-07 08:30:00', 1, 'completed'),
(12, 3, 'Discontinue NSAIDs / Blood Thinners', 'patient_action', 'Stop aspirin/ibuprofen.', '2026-08-05 08:30:00', 1, 'completed'),
-- Schedule 4 (Ananya Sen - Colonoscopy)
(13, 4, 'Liquid Prep Diet Compliance', 'patient_action', 'Bowel prep drink.', '2026-08-13 14:00:00', 1, 'pending'),
(14, 4, 'Confirm Escort Driver Present', 'patient_action', 'Driver name/phone.', '2026-08-14 13:00:00', 0, 'pending'),
(15, 4, 'Sign Colonoscopy Consent Form', 'patient_action', 'Verify signed consent.', '2026-08-14 13:30:00', 1, 'pending'),
-- Schedule 7 (Meera Desai - Gallbladder)
(16, 7, 'Upload Blood Sugar / HbA1c Profile', 'document_upload', 'Blood test results.', '2026-08-15 09:00:00', 1, 'completed'),
(17, 7, 'Fasting (NPO)', 'patient_action', 'Fasting from midnight.', '2026-08-18 01:00:00', 1, 'pending');

-- 8. Seed Uploaded Reports
INSERT INTO `tbl_uploaded_reports` (`id`, `checklist_item_id`, `file_name`, `file_path`, `file_size_bytes`) VALUES
(2, 11, 'knee_mri_rahul_verma.jpg', '/secure_uploads/tbl_procedures/3/checklist_11/knee_mri_rahul_verma.jpg', 2450000),

-- 9. Seed Procedure Readiness
INSERT INTO `tbl_procedure_readiness` (`id`, `scheduled_procedure_id`, `readiness_status`, `evaluated_by_user_id`, `notes`) VALUES
(1, 1, 'red', 3, 'Critical ECG report upload is pending.'),
(2, 2, 'red', 3, 'Fasting pending. ECG upload overdue. High risk due to glucose (175 mg/dL).'),
(3, 3, 'green', 4, 'Critical scans uploaded, blood match secured, and NSAID suspension confirmed.'),
(4, 4, 'orange', 5, 'Sedation escort details not yet provided by patient.'),
(5, 5, 'red', 5, 'Initial scheduling. Bowel prep instructions pending verification.'),
(6, 6, 'yellow', 6, 'Awaiting antibiotic drops initiation verification.'),
(7, 7, 'red', 7, 'Elevated body temperature (100.2 F) and creatinine (1.40 mg/dL). Review required.'),
(8, 8, 'red', 3, 'Initial creation. Dynamic checklist requirements initialized.');

-- 10. Seed Health Suggestions
INSERT INTO `tbl_health_suggestions` (`id`, `procedure_id`, `suggestion_text`, `trigger_condition`) VALUES
(1, 1, 'Discontinue Metformin 48 hours prior to contrast dye to prevent kidney injury.', 'diabetic'),
(2, 1, 'Keep your cardiac device card (Pacemaker/ICD) on your person at admission.', 'cardiac_history'),
(3, 2, 'Ensure someone is available at home to assist you for the first 3 days post-surgery.', 'all'),
(4, 3, 'Avoid eating red or purple-colored gelatin or liquids 24 hours prior to colonoscopy.', 'all'),
(5, 5, 'Do not lift weights heavier than 5kg for at least 4 weeks post Lap-Chole.', 'all');

-- 11. Seed Risk Alerts
INSERT INTO `tbl_risk_alerts` (`id`, `scheduled_procedure_id`, `alert_type`, `alert_message`, `severity`, `is_resolved`) VALUES
(1, 2, 'DIABETIC_GLUCOSE_WARNING', 'Patient blood sugar is 175.0 mg/dL. Monitor and hold insulin as directed.', 'high', 0),
(2, 2, 'ECG_OVERDUE', 'Critical ECG lab report upload is overdue by 24+ hours.', 'high', 0),
(3, 7, 'CREATININE_ELEVATED', 'Patient creatinine (1.40 mg/dL) indicates potential renal strain.', 'high', 0),
(4, 7, 'FEVER_WARNING', 'Patient temperature is elevated (100.2 F) which may indicate infection.', 'medium', 0);

-- 12. Seed Notifications
INSERT INTO `tbl_notifications` (`id`, `user_id`, `title`, `message`, `type`, `status`) VALUES
(1, 8, 'Procedure Scheduled', 'Your Left Heart Catheterization has been scheduled for Aug 10, 2026.', 'in_app', 'read'),
(2, 9, 'Preparation Alert', 'Please upload your ECG report to fulfill your checklist requirements.', 'sms', 'unread'),
(3, 9, 'Fasting Reminder', 'Your fasting window starts on Aug 10 at 3:30 AM.', 'email', 'unread'),
(4, 10, 'Blood Match Secured', 'Blood bank reserves have been matched and verified for your surgery.', 'in_app', 'read'),
(5, 11, 'Escort Required', 'Please log details of your responsible escort driver in the portal.', 'in_app', 'unread');
