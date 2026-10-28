-- =========================================================================
-- Hospital Procedure Preparation and Readiness System - Database Schema
-- Database Engine: InnoDB | Character Set: utf8mb4 | Collation: utf8mb4_unicode_ci
-- =========================================================================

-- Create Database
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
-- Description: Stores system security groups (RBAC).
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
-- Description: Core authentication credentials and names for all actors.
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
-- Description: Specialized clinical metadata extending the `tbl_users` table for doctors.
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
-- Description: Sensitive clinical metadata extending the `tbl_users` table for patients.
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
-- Description: Reference catalog of surgical operations or medical tbl_procedures.
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
-- Description: Dynamic templates of checklist tasks mapped to procedure catalog codes.
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
-- Description: Schedule linking patients, surgeons, locations, and time slots.
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
-- Description: Tasks generated from preparation rules for each scheduled procedure.
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
-- Description: File metadata associated with checklist item document uploads.
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
-- Description: Calculated readiness state (Red, Yellow, Green) for surgery slots.
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
-- Description: Health instructions associated with specific procedure definitions.
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
-- Description: Warnings generated dynamically (e.g. overdue critical pre-ops).
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
-- Description: Communications queue for patients and providers.
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
-- Description: Records pre-op lab values for validation warnings.
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

-- 2. Seed Users
-- Passwords are set to simulated bcrypt hashes of 'Password123!'
INSERT INTO `tbl_users` (`id`, `role_id`, `username`, `email`, `password_hash`, `first_name`, `last_name`, `phone`, `is_active`) VALUES
(1, 1, 'admin_clara', 'clara.admin@hospital.org', '$2b$12$Kk9GzKkX6c.Oq3nIuXNf.O9wF7vDbeO4Vskm73fM.2P/yUjKj1rE.', 'Clara', 'Windsor', '+15550100', 1),
(3, 3, 'doctor_robert', 'robert.surgeon@hospital.org', '$2b$12$Kk9GzKkX6c.Oq3nIuXNf.O9wF7vDbeO4Vskm73fM.2P/yUjKj1rE.', 'Robert', 'Chen', '+15550102', 1),
(4, 4, 'patient_john', 'john.doe@patient.net', '$2b$12$Kk9GzKkX6c.Oq3nIuXNf.O9wF7vDbeO4Vskm73fM.2P/yUjKj1rE.', 'John', 'Doe', '+15550103', 1),
(5, 4, 'patient_alice', 'alice.smith@patient.net', '$2b$12$Kk9GzKkX6c.Oq3nIuXNf.O9wF7vDbeO4Vskm73fM.2P/yUjKj1rE.', 'Alice', 'Smith', '+15550104', 1);

-- 3. Seed Doctor Profiles
INSERT INTO `tbl_doctor_profiles` (`id`, `user_id`, `license_number`, `specialty`, `department`) VALUES
(1, 3, 'LIC-MD-99214', 'Cardiology / Electrophysiology', 'Cardiovascular Sciences');

-- 4. Seed Patient Profiles
INSERT INTO `tbl_patient_profiles` (`id`, `user_id`, `date_of_birth`, `gender`, `blood_type`, `medical_history`, `emergency_contact_name`, `emergency_contact_phone`) VALUES
(1, 4, '1980-05-15', 'male', 'A+', 'Hypertension, Mild Seasonal Allergies', 'Jane Doe', '+15550999'),
(2, 5, '1992-11-23', 'female', 'O-', 'Type-2 Diabetes', 'David Smith', '+15550888');

-- 5. Seed Procedures
INSERT INTO `tbl_procedures` (`id`, `code`, `name`, `description`, `category`, `est_duration_mins`) VALUES
(1, 'CPT-93452', 'Left Heart Catheterization', 'Diagnostic assessment of blood flow and pressure within chambers of the left heart.', 'Cardiology', 75),
(2, 'CPT-45378', 'Colonoscopy', 'Endoscopic examination of the large bowel and the distal part of the small bowel.', 'Gastroenterology', 45);

-- 5b. Seed Dynamic Checklist Templates
INSERT INTO `tbl_dynamic_checklist_templates` (`procedure_id`, `task_name`, `task_type`, `description`, `due_days_before`, `is_critical`) VALUES
(1, 'NPO Fasting (No food or water)', 'patient_action', 'Fasting is required for at least 8 hours prior to the heart catheterization.', 1, 1),
(1, 'Stop Anticoagulant (Blood Thinners)', 'patient_action', 'Temporarily suspend blood thinning medications 48 hours prior to procedure as advised by physician.', 2, 1),
(1, 'Upload Recent ECG Lab Report', 'document_upload', 'Please upload a PDF or image copy of your 12-lead ECG conducted in the last 14 days.', 3, 1),
(1, 'Clinical Consent Form Signature', 'staff_verification', 'Verify that the physical surgical consent documentation has been signed by patient and surgeon.', 0, 1),
(2, 'Liquid Prep Diet Compliance', 'patient_action', 'Complete gastroenterologist-approved colon cleansing prep formulation.', 1, 1),
(2, 'Confirm Escort Driver Present', 'patient_action', 'Provide details of the responsible adult driving you home after sedation.', 0, 0);

-- 6. Seed Scheduled Procedures
INSERT INTO `tbl_scheduled_procedures` (`id`, `patient_id`, `doctor_id`, `procedure_id`, `scheduled_at`, `location`, `status`) VALUES
(1, 4, 3, 1, '2026-08-20 09:00:00', 'Catheterization Lab 3', 'scheduled'),
(2, 5, 3, 2, '2026-08-21 11:30:00', 'Endoscopy Suite B', 'scheduled');

-- 7. Seed Checklist Items (Linked to Schedule 1)
INSERT INTO `tbl_checklist_items` (`id`, `scheduled_procedure_id`, `task_name`, `task_type`, `description`, `due_by_datetime`, `is_critical`, `status`) VALUES
(1, 1, 'NPO Fasting (No food or water)', 'patient_action', 'Fasting is required for at least 8 hours prior to the heart catheterization.', '2026-08-20 01:00:00', 1, 'pending'),
(2, 1, 'Stop Anticoagulant (Blood Thinners)', 'patient_action', 'Temporarily suspend blood thinning medications 48 hours prior to procedure as advised by physician.', '2026-08-18 09:00:00', 1, 'completed'),
(3, 1, 'Upload Recent ECG Lab Report', 'document_upload', 'Please upload a PDF or image copy of your 12-lead ECG conducted in the last 14 days.', '2026-08-17 17:00:00', 1, 'pending'),
(4, 1, 'Clinical Consent Form Signature', 'staff_verification', 'Verify that the physical surgical consent documentation has been signed by patient and surgeon.', '2026-08-20 08:30:00', 1, 'pending');

-- 8. Seed Checklist Items (Linked to Schedule 2)
INSERT INTO `tbl_checklist_items` (`id`, `scheduled_procedure_id`, `task_name`, `task_type`, `description`, `due_by_datetime`, `is_critical`, `status`) VALUES
(5, 2, 'Liquid Prep Diet Compliance', 'patient_action', 'Complete gastroenterologist-approved colon cleansing prep formulation.', '2026-08-20 18:00:00', 1, 'pending'),
(6, 2, 'Confirm Escort Driver Present', 'patient_action', 'Provide details of the responsible adult driving you home after sedation.', '2026-08-21 10:30:00', 0, 'pending');

-- 9. Seed Uploaded Reports and update checklist status
UPDATE `tbl_checklist_items` SET `status` = 'completed', `completed_by_user_id` = 4, `completed_at` = '2026-08-17 14:32:00' WHERE `id` = 3;

INSERT INTO `tbl_uploaded_reports` (`id`, `checklist_item_id`, `file_name`, `file_path`, `file_size_bytes`) VALUES
(1, 3, 'ecg_report_john_doe.pdf', '/secure_uploads/tbl_procedures/1/checklist_3/ecg_report_john_doe.pdf', 1245000);

-- 10. Seed Procedure Readiness
INSERT INTO `tbl_procedure_readiness` (`id`, `scheduled_procedure_id`, `readiness_status`, `evaluated_by_user_id`, `notes`) VALUES
(1, 1, 'red', 3, 'Pending patient NPO verification and clinician signature on consent form.'),
(2, 2, 'red', 3, 'Initial creation. Waiting for patient to begin prep.');

-- 11. Seed Health Suggestions
INSERT INTO `tbl_health_suggestions` (`id`, `procedure_id`, `suggestion_text`, `trigger_condition`) VALUES
(1, 1, 'Discontinue Metformin 48 hours prior to contrast dye exposure to prevent kidney injury.', 'diabetic'),
(2, 1, 'Keep your cardiac device card (Pacemaker/ICD) on your person during hospital check-in.', 'cardiac_history'),
(3, 2, 'Avoid eating red-colored gelatin, popsicles, or beverages 24 hours prior to colonoscopy.', 'all');

-- 12. Seed Risk Alerts
INSERT INTO `tbl_risk_alerts` (`id`, `scheduled_procedure_id`, `alert_type`, `alert_message`, `severity`, `is_resolved`) VALUES
(1, 1, 'ECG_UNVERIFIED', 'ECG document uploaded by patient but awaiting clinician validation.', 'medium', 0);

-- 13. Seed Notifications
INSERT INTO `tbl_notifications` (`id`, `user_id`, `title`, `message`, `type`, `status`) VALUES
(1, 4, 'Procedure Scheduled', 'Your Heart Catheterization has been scheduled for Aug 20, 2026 at 9:00 AM.', 'in_app', 'read'),
(2, 4, 'Preparation Task Alert', 'Please upload your ECG report by Aug 17, 2026.', 'sms', 'unread');
